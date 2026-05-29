import os
import requests
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
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
token = jwt.encode(payload, secret, algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

nuevo_esp = {
    'caso_id': 1,
    'especialidad_id': 1,
    'descartado': False,
    'especialidad_nombre': "Cardiología"
}
r1 = requests.post(f"{API_BASE_URL}/api/caso_clinico_especialidad", json=nuevo_esp, headers=headers)
print("Crear esp:")
print(f"Status: {r1.status_code}")
print(r1.text)
