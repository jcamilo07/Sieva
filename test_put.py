import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('http://localhost:5034/api/casos_clinicos/1', 
                             method='PUT', 
                             data=json.dumps({"calificacion_ia": 3, "observacion": "Test"}).encode('utf-8'),
                             headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, context=ctx) as f:
        print(f.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
