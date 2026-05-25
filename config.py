"""
config.py - Configuracion centralizada de la aplicacion Flask.
"""

import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# URL base de la API REST que consume este frontend. Debe ser el
# servicio PostgreSQL genérico al que está conectado.
API_BASE_URL = os.getenv("API_BASE_URL", "http://sieva-frontend.runasp.net")

# Clave secreta para el manejo de sesiones y mensajes flash.
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-flask-frontend-2024")

# Clave secreta para firmar el JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret-key-2026")

# Credenciales de los 2 administradores definidas en el entorno
ADMINS = {
    os.getenv("ADMIN1_EMAIL", "jpablolujanborraez@gmail.com"): os.getenv("ADMIN1_PASSWORD", "$2b$12$e3mQss2M176GWnZXumbYDeau.D9ahFVruCzubORBRCqcZvJdN7qWO"),
    os.getenv("ADMIN2_EMAIL", "juancamiloblanquiceth10@gmail.com"): os.getenv("ADMIN2_PASSWORD", "$2b$12$zLD9hmSkKXzhfs2XhcmEBOg1yigx/wZx.jDWzO6V2ruinkwTuLSZu")
}

# SMTP (configurar para recuperacion de contrasena)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "juancamiloblanquiceth10@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "kgym mfnp ahqm jfok")
SMTP_FROM = os.getenv("SMTP_FROM", "juancamiloblanquiceth10@gmail.com")