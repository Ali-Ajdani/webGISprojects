from pysimplesoap.client import SoapClient

client = SoapClient(
    location="http://127.0.0.1:8000/",
    action="http://127.0.0.1:8000/",
    namespace="http://example.com/geotriangle.wsdl",
    soap_ns="soap",
    trace=True,
    ns=True
)

# Call TrianglePerimeter for 3 sample points (IDs 1,2,3)
result = client.TrianglePerimeter(id1=1, id2=2, id3=3)

print("Perimeter (meters):", result.perimeter_m)
