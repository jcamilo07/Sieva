import requests
from datetime import datetime
from services.auth_service import AuthService
from services.api_service import ApiService
import json

base_url = "http://localhost:5034"
auth = AuthService()
token = auth._get_admin_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

import os
# 1. Crear el usuario juancamiloblanquiceth10@gmail.com con clave (usar variable de entorno o input manual)
password_admin = os.environ.get("ADMIN1_PASSWORD_PLAIN", "INGRESE_PASSWORD_AQUI")
usuario = {
    "nombre": "Juan Camilo Blanquiceth",
    "email": "juancamiloblanquiceth10@gmail.com",
    "password_hash": password_admin,
    "activo": True
}
print("Creando usuario...")
res_usuario = requests.post(f"{base_url}/api/usuarios?camposEncriptar=password_hash", json=usuario, headers=headers)
print("Estado creación usuario:", res_usuario.status_code)

try:
    print(res_usuario.json())
except:
    pass

# 2. Obtener el ID del usuario recién creado
res_users = requests.get(f"{base_url}/api/usuarios", headers=headers)
usuarios = res_users.json().get("datos", [])
usuario_id = next((u["id"] for u in usuarios if u["email"] == "juancamiloblanquiceth10@gmail.com"), None)

if not usuario_id:
    print("No se pudo obtener el ID del usuario.")
    exit(1)

# 3. Obtener el ID del rol Administrador
res_roles = requests.get(f"{base_url}/api/roles", headers=headers)
roles = res_roles.json().get("datos", [])
rol_id = next((r["id"] for r in roles if r["nombre"] == "Administrador"), None)

if not rol_id:
    print("No se encontró el rol Administrador.")
    exit(1)

# 4. Asignar el rol al usuario
asignacion = {
    "usuario_id": usuario_id,
    "rol_id": rol_id
}
print("Asignando rol Administrador...")
res_rol = requests.post(f"{base_url}/api/usuario_rol", json=asignacion, headers=headers)
print("Estado asignación rol:", res_rol.status_code)
try:
    print(res_rol.json())
except:
    pass

print("Proceso finalizado.")
