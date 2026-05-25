import requests

base_url = "http://localhost:5034"
res = requests.get(f"{base_url}/api/database/inspect/casos_clinicos")
print(f"Columnas de casos_clinicos:")
try:
    cols = res.json()
    for c in cols:
        print(f"  - {c['name']} ({c['type']})")
except:
    print("Error")
