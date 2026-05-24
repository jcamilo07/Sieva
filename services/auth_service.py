import requests
import random
import string
from flask import session
from services.api_service import ApiService
from config import API_BASE_URL
from utils.email_service import enviar_correo_recuperacion

# Variable en memoria para registrar usuarios que deben cambiar contrasena obligatoriamente
_emails_debe_cambiar = set()

class AuthService:
    def __init__(self):
        self.base_url = API_BASE_URL

    def login_usuario(self, email, password):
        """
        Realiza el proceso de login en 3 pasos:
        1. Llama a la API genérica para validar credenciales y obtener el JWT.
        2. Usa el JWT para obtener los roles del usuario (consulta JOIN).
        3. Guarda el JWT, el usuario y los roles en la sesión de Flask.
        """
        url_login = f"{self.base_url}/api/autenticacion/token"
        
        payload_login = {
            "tabla": "usuarios",
            "campoUsuario": "email",
            "campoContrasena": "password_hash",
            "usuario": email,
            "contrasena": password
        }

        try:
            # Paso 1: Autenticación
            res_login = requests.post(url_login, json=payload_login)
            
            if res_login.status_code == 404:
                return False, "Usuario no encontrado."
            elif res_login.status_code == 401:
                return False, "Contraseña incorrecta."
            elif not res_login.ok:
                return False, "Error al autenticar."
                
            data = res_login.json()
            token = data.get("token")
            
            if not token:
                return False, "No se recibió el token de seguridad."

            # Paso 2: Obtener roles
            url_consulta = f"{self.base_url}/api/consultas/ejecutarconsultaparametrizada"
            consulta_roles = """
                SELECT r.nombre 
                FROM roles r
                INNER JOIN usuario_rol ur ON r.id = ur.rol_id
                INNER JOIN usuarios u ON u.id = ur.usuario_id
                WHERE u.email = @email
            """
            payload_consulta = {
                "consulta": consulta_roles,
                "parametros": {"@email": email}
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            res_roles = requests.post(url_consulta, json=payload_consulta, headers=headers)
            
            roles = []
            if res_roles.ok:
                data_roles = res_roles.json()
                resultados = data_roles.get("resultados") or data_roles.get("Resultados") or []
                roles = [r.get("nombre") for r in resultados]
                
            # Paso 3: Configurar sesión
            session.clear() # Limpiar cualquier sesión previa
            session['jwt_token'] = token
            session['usuario'] = email
            session['roles'] = roles
            
            # Verificar si debe cambiar la contrasena
            if email in _emails_debe_cambiar:
                session['debe_cambiar_contrasena'] = True
            
            return True, "Login exitoso"
            
        except requests.RequestException as e:
            return False, f"Error de conexión con el servidor: {e}"

    def logout_usuario(self):
        """Limpia la sesión del usuario actual."""
        session.clear()

    def _get_admin_token(self):
        """Genera un token de administrador localmente firmado, evitando depender de contraseñas de la BD."""
        try:
            import jwt
            from datetime import datetime, timedelta, timezone
            
            import os
            # Usar la misma clave y configuración definida en el appsettings.json de la API C#
            secret = os.environ.get("JWT_SECRET_KEY", "MySuperSecretKey1234567890!@#$%^&*()_+")
            payload = {
                "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "admin_maestro@sieva.com",
                "tabla": "usuarios",
                "campoUsuario": "email",
                "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
                "iss": "MyApp",
                "aud": "MyAppUsers"
            }
            return jwt.encode(payload, secret, algorithm="HS256")
        except Exception as e:
            print(f"Error generando token maestro: {e}")
            return None

    def recuperar_contrasena(self, email):
        """
        Inicia el proceso de recuperación de contraseña.
        Genera una temporal, la actualiza en BD, y la envía por SMTP.
        """
        # Generar contrasena temporal (10 caracteres, letras y digitos)
        caracteres = string.ascii_letters + string.digits
        temp_pass = ''.join(random.choice(caracteres) for i in range(10))
        
        # Como no hay sesión activa, necesitamos un token de admin para actualizar
        admin_token = self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        
        url_actualizar = f"{self.base_url}/api/usuarios/email/{email}?camposEncriptar=password_hash"
        
        try:
            res = requests.put(url_actualizar, json={"password_hash": temp_pass}, headers=headers)
            
            # Intentar decodificar JSON o mostrar estado
            try:
                mensaje = res.json().get("mensaje", "Operacion completada.")
            except ValueError:
                mensaje = f"Error HTTP {res.status_code}"
                
            if not res.ok:
                return False, f"No se pudo generar la contraseña: {mensaje}"
        except Exception as e:
            return False, f"Error de conexión al actualizar contraseña: {str(e)}"
            
        # Marcar al usuario para cambio obligatorio
        _emails_debe_cambiar.add(email)
        
        # Enviar correo
        correo_enviado, msj_correo = enviar_correo_recuperacion(email, temp_pass)
        
        if correo_enviado:
            return True, "Se ha enviado una contraseña temporal a su correo electrónico."
        else:
            # Si el correo falla, devolvemos la contraseña para mostrarla en desarrollo
            return True, f"Modo Desarrollo - SMTP no configurado. Tu contraseña temporal es: {temp_pass}"

    def actualizar_contrasena(self, email, nueva_contrasena):
        """
        Actualiza la contrasena del usuario y remueve el flag de cambio obligatorio.
        """
        api = ApiService()
        exito, mensaje = api.actualizar(
            "usuarios", 
            "email", 
            email, 
            {"password_hash": nueva_contrasena}, 
            campos_encriptar="password_hash"
        )
        
        if exito:
            # Remover de la lista de obligados
            if email in _emails_debe_cambiar:
                _emails_debe_cambiar.remove(email)
            return True, "Contraseña actualizada exitosamente."
        else:
            return False, f"Error al actualizar la contraseña: {mensaje}"

    def esta_autenticado(self):
        """Verifica si el usuario tiene una sesión activa."""
        return 'jwt_token' in session
        
    def tiene_rol(self, rol_requerido):
        """Verifica si el usuario actual tiene el rol solicitado."""
        roles = session.get('roles', [])
        return rol_requerido in roles
