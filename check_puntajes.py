import os
os.environ["API_BASE_URL"] = "http://localhost:5034"
from services.auth_service import AuthService
import requests

auth = AuthService()
admin_token = auth._get_admin_token()
headers = {"Authorization": f"Bearer {admin_token}"}

res = requests.get("http://localhost:5034/api/puntajes_casos", headers=headers)
print("Status:", res.status_code)
print("Text:", res.text)
