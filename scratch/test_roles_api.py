import requests

url_login = "http://localhost:5034/api/autenticacion/token"
import os
payload_login = {
    "tabla": "usuarios",
    "campoUsuario": "email",
    "campoContrasena": "password_hash",
    "usuario": "juancamiloblanquiceth10@gmail.com",
    "contrasena": os.environ.get("TEST_PASSWORD", "INGRESE_PASSWORD_AQUI")
}

try:
    print("1. Intentando login...")
    res_login = requests.post(url_login, json=payload_login)
    print("Status:", res_login.status_code)
    data = res_login.json()
    token = data.get("token")
    print("Token recibido:", token is not None)
    
    if token:
        # Paso 2: Obtener roles
        url_consulta = "http://localhost:5034/api/consultas/ejecutarconsultaparametrizada"
        # En Postgres, a veces los nombres de columnas o parámetros requieren comillas o sintaxis específica
        # como :email o @email.
        consulta_roles = """
            SELECT r.nombre 
            FROM roles r
            INNER JOIN usuario_rol ur ON r.id = ur.rol_id
            INNER JOIN usuarios u ON u.id = ur.usuario_id
            WHERE u.email = @email
        """
        payload_consulta = {
            "consulta": consulta_roles,
            "parametros": {"@email": "juancamiloblanquiceth10@gmail.com"}
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        print("\n2. Consultando roles...")
        res_roles = requests.post(url_consulta, json=payload_consulta, headers=headers)
        print("Status roles:", res_roles.status_code)
        print("Respuesta roles:", res_roles.text)
except Exception as e:
    print("Error:", e)
