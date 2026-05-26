import os
import requests
import jwt
from datetime import datetime, timedelta, timezone

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5034")

secret = "MySuperSecretKey1234567890!@#$%^&*()_+"
payload = {
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "admin_maestro@sieva.com",
    "tabla": "usuarios",
    "campoUsuario": "email",
    "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    "iss": "MyApp",
    "aud": "MyAppUsers"
}
admin_token = jwt.encode(payload, secret, algorithm="HS256")
headers = {"Authorization": f"Bearer {admin_token}"}

url = f"{API_BASE_URL}/api/usuarios"
res = requests.get(url, headers=headers)
print("Usuarios:", res.json())

url_roles = f"{API_BASE_URL}/api/roles"
res_roles = requests.get(url_roles, headers=headers)
print("Roles:", res_roles.json())

url_ur = f"{API_BASE_URL}/api/usuario_rol"
res_ur = requests.get(url_ur, headers=headers)
print("Usuario-Rol:", res_ur.json())

url_me = f"{API_BASE_URL}/api/medico_experto"
res_me = requests.get(url_me, headers=headers)
print("Medico Experto:", res_me.text)
