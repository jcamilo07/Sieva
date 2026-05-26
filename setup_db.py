import os
import requests
from config import API_BASE_URL
from services.auth_service import AuthService
from services.api_service import ApiService

def init_db():
    print(f"Usando API_BASE_URL: {API_BASE_URL}")
    import jwt
    from datetime import datetime, timedelta, timezone
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
    if not admin_token:
        print("Error al generar token maestro.")
        return

    headers = {"Authorization": f"Bearer {admin_token}"}

    api = ApiService()
    api._get_headers = lambda: headers

    # 1. Obtener usuarios actuales
    print("Obteniendo usuarios actuales...")
    usuarios = api.listar("usuarios")
    for u in usuarios:
        print(f"Eliminando usuario {u.get('email')} (ID: {u.get('id')})")
        api.eliminar("usuarios", "id", u.get("id"))

    # 2. Obtener roles actuales y limpiar
    print("Obteniendo roles actuales...")
    roles = api.listar("roles")
    for r in roles:
        if r["nombre"] == "Medico experto":
            print(f"Eliminando rol {r['nombre']}")
            api.eliminar("roles", "id", r["id"])

    roles = api.listar("roles")
    roles_dict = {r["nombre"]: r["id"] for r in roles}

    if "Administrador" not in roles_dict:
        print("Creando rol Administrador...")
        api.crear("roles", {"nombre": "Administrador", "descripcion": "Acceso total al sistema"})
    
    if "Medico" not in roles_dict:
        print("Creando rol Medico...")
        api.crear("roles", {"nombre": "Medico", "descripcion": "Médico general"})

    roles = api.listar("roles")
    roles_dict = {r["nombre"]: r["id"] for r in roles}

    # 3. Crear usuarios
    usuarios_nuevos = [
        {
            "nombre": "Carlos Manuel Castro Londoño",
            "email": "cmanuel.castro@udea.edu.co",
            "password_raw": "@Manuel876",
            "rol": "Medico"
        },
        {
            "nombre": "Carlos Arturo Castro",
            "email": "carlos.castro@usbmed.edu.co",
            "password_raw": "@Ccastro441",
            "rol": "Administrador"
        }
    ]

    usuarios_con_hash = [
        {
            "nombre": "Juan Pablo Lujan",
            "email": "jpablolujanborraez@gmail.com",
            "password_hash": "$2b$12$e3mQss2M176GWnZXumbYDeau.D9ahFVruCzubORBRCqcZvJdN7qWO",
            "rol": "Administrador"
        },
        {
            "nombre": "Juan Camilo Blanquiceth",
            "email": "juancamiloblanquiceth10@gmail.com",
            "password_hash": "$2b$12$zLD9hmSkKXzhfs2XhcmEBOg1yigx/wZx.jDWzO6V2ruinkwTuLSZu",
            "rol": "Administrador"
        }
    ]

    # Crear usuarios con contraseñas crudas (se encriptan en el backend)
    for u in usuarios_nuevos:
        print(f"Creando usuario (raw password): {u['nombre']}...")
        datos_usuario = {
            "nombre": u["nombre"],
            "email": u["email"],
            "password_hash": u["password_raw"]
        }
        exito, msg = api.crear("usuarios", datos_usuario, campos_encriptar="password_hash")
        print(f"Resultado crear {u['email']}: {exito} - {msg}")

        users = api.listar("usuarios")
        user_id = next((usr["id"] for usr in users if usr["email"] == u["email"]), None)
        
        if user_id:
            api.crear("usuario_rol", {"usuario_id": user_id, "rol_id": roles_dict[u["rol"]]})

    # Crear usuarios con hashes existentes (sin encriptar de nuevo)
    for u in usuarios_con_hash:
        print(f"Creando usuario (hash existente): {u['nombre']}...")
        datos_usuario = {
            "nombre": u["nombre"],
            "email": u["email"],
            "password_hash": u["password_hash"]
        }
        exito, msg = api.crear("usuarios", datos_usuario)
        print(f"Resultado crear {u['email']}: {exito} - {msg}")

        users = api.listar("usuarios")
        user_id = next((usr["id"] for usr in users if usr["email"] == u["email"]), None)
        
        if user_id:
            api.crear("usuario_rol", {"usuario_id": user_id, "rol_id": roles_dict[u["rol"]]})

    print("Proceso finalizado con éxito.")

if __name__ == "__main__":
    init_db()
