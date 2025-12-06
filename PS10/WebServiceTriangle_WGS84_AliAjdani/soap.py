from pysimplesoap.server import SoapDispatcher, SOAPHandler
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qs
import math

# ------------------------
# 1) data
# ------------------------

# WGS84 mean Earth radius (meters)
EARTH_RADIUS = 6371008.8

# predefined points list
# X = longitude (deg), Y = latitude (deg)
points = [
    {"ID": 1, "X": 51.1, "Y": 35.5},
    {"ID": 2, "X": 52.3, "Y": 34.3},
    {"ID": 3, "X": 53.2, "Y": 32.3},
    {"ID": 4, "X": 49.9, "Y": 35.7},
]
# ------------------------
# 2) helper functions
# ------------------------

def get_by_id(point_id):
    """Return a point dict by ID, or None if not found."""
    for pt in points:
        if pt["ID"] == point_id:
            return pt
    return None


def haversine(lat1, lon1, lat2, lon2):
    """
    Great-circle distance between two WGS84 points (Haversine).
    Inputs in degrees, output in meters.
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        dlon / 2
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS * c
# ------------------------
# 3) web methods (SOAP operations)
# ------------------------

def GetPointbyID(point_id):
    """Return a point (ID, X, Y) by its ID."""
    pt = get_by_id(point_id)
    if pt is None:
        return {"ID": 0, "X": 0.0, "Y": 0.0}
    return pt


def TrianglePerimeter(id1, id2, id3):
    """
    Compute the perimeter of a triangle defined by
    three points selected from the list using WGS84.
    """
    p1 = get_by_id(id1)
    p2 = get_by_id(id2)
    p3 = get_by_id(id3)

    if p1 is None or p2 is None or p3 is None:
        return 0.0

    # note: Y = lat, X = lon
    d12 = haversine(p1["Y"], p1["X"], p2["Y"], p2["X"])
    d23 = haversine(p2["Y"], p2["X"], p3["Y"], p3["X"])
    d31 = haversine(p3["Y"], p3["X"], p1["Y"], p1["X"])

    perimeter = d12 + d23 + d31
    return perimeter
# ------------------------
# 4) dispatcher
# ------------------------

dispatcher = SoapDispatcher(
    name="GeoTriangleService",
    location="http://127.0.0.1:8000/",
    action="http://127.0.0.1:8000/",
    namespace="http://example.com/geotriangle.wsdl",
    trace=True,
    ns=True,
)

dispatcher.register_function(
    name="GetPointbyID",
    fn=GetPointbyID,
    returns={"ID": int, "X": float, "Y": float},
    args={"point_id": int},
)

dispatcher.register_function(
    name="TrianglePerimeter",
    fn=TrianglePerimeter,
    returns={"perimeter_m": float},
    args={"id1": int, "id2": int, "id3": int},
)
# ------------------------
# 5) request handler
# ------------------------

class SOAPRequestHandler(SOAPHandler):
    def do_GET(self):
        # WSDL: http://127.0.0.1:8000/?wsdl
        parsed_path = urlparse(self.path)
        path = parsed_path.path.strip("/")
        query_params = parse_qs(parsed_path.query)

        if path == "" and ("wsdl" in query_params or not query_params):
            wsdl_xml = dispatcher.wsdl()
            self.send_response(200)
            self.send_header("Content-type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(wsdl_xml)))
            self.end_headers()
            self.wfile.write(wsdl_xml)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        data_bytes = self.rfile.read(int(self.headers["content-length"]))
        data = data_bytes.decode("utf-8")

        response = dispatcher.dispatch(data)

        self.send_response(200)
        self.send_header("Content-type", "text/xml; charset=utf-8")
        self.end_headers()
        self.wfile.write(response)
# ------------------------
# 6) main server loop
# ------------------------

if __name__ == "__main__":
    httpd = HTTPServer(("127.0.0.1", 8000), SOAPRequestHandler)
    print("GeoTriangle SOAP service running at http://127.0.0.1:8000/")
    print("WSDL: http://127.0.0.1:8000/?wsdl")
    httpd.serve_forever()
