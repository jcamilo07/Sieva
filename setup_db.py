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
    # Hack para que api_service use el admin_token en lugar de session
    api._get_headers = lambda: headers

    # 1. Obtener usuarios actuales
    print("Obteniendo usuarios actuales...")
    usuarios = api.listar("usuarios")
    for u in usuarios:
        print(f"Eliminando usuario {u.get('email')} (ID: {u.get('id')})")
        api.eliminar("usuarios", "id", u.get("id"))

    # 2. Obtener roles actuales y limpiar si es necesario
    print("Obteniendo roles actuales...")
    roles = api.listar("roles")
    roles_dict = {r["nombre"]: r["id"] for r in roles}

    if "Administrador" not in roles_dict:
        print("Creando rol Administrador...")
        api.crear("roles", {"nombre": "Administrador", "descripcion": "Acceso total al sistema"})
    
    if "Medico experto" not in roles_dict:
        print("Creando rol Medico experto...")
        api.crear("roles", {"nombre": "Medico experto", "descripcion": "Médico experto con acceso a casos"})

    # Volver a obtener roles para tener sus IDs
    roles = api.listar("roles")
    roles_dict = {r["nombre"]: r["id"] for r in roles}

    # 3. Crear usuarios
    usuarios_a_crear = [
        {
            "nombre": "Carlos Manuel Castro Londoño",
            "email": "cmanuel.castro@udea.edu.co",
            "password_hash": "@Manuel876",
            "rol": "Medico experto"
        },
        {
            "nombre": "Carlos Arturo Castro",
            "email": "carlos.castro@usbmed.edu.co",
            "password_hash": "@Ccastro441",
            "rol": "Administrador"
        }
    ]

    for u in usuarios_a_crear:
        print(f"Creando usuario: {u['nombre']}...")
        datos_usuario = {
            "nombre": u["nombre"],
            "email": u["email"],
            "password_hash": u["password_hash"]
        }
        exito, msg = api.crear("usuarios", datos_usuario, campos_encriptar="password_hash")
        print(f"Resultado crear {u['email']}: {exito} - {msg}")

        # Obtener el id del usuario recién creado
        users = api.listar("usuarios")
        user_id = None
        for usr in users:
            if usr["email"] == u["email"]:
                user_id = usr["id"]
                break
        
        if user_id:
            rol_id = roles_dict[u["rol"]]
            print(f"Asignando rol {u['rol']} (ID: {rol_id}) al usuario ID: {user_id}...")
            # En la tabla usuario_rol
            api.crear("usuario_rol", {
                "usuario_id": user_id,
                "rol_id": rol_id
            })
        else:
            print("No se pudo obtener el ID del usuario recién creado para asignarle el rol.")

    print("Proceso finalizado con éxito.")

if __name__ == "__main__":
    init_db()
