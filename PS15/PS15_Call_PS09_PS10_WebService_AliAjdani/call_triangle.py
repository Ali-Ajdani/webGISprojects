import requests

url = "http://localhost:44357/TriangleService.asmx"

soap_body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TrianglePerimeter xmlns="http://tempuri.org/">
      <a>3</a>
      <b>4</b>
      <c>5</c>
    </TrianglePerimeter>
  </soap:Body>
</soap:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "http://tempuri.org/TrianglePerimeter"
}

resp = requests.post(url, data=soap_body.encode("utf-8"), headers=headers, timeout=10)

print("status:", resp.status_code)
print(resp.text)
