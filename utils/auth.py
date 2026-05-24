import jwt
import datetime
from config import JWT_SECRET_KEY

def generar_token(email):
    """Genera un token JWT para el usuario proporcionado."""
    payload = {
        'sub': email,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verificar_token(token):
    """
    Verifica la validez de un token JWT.
    Retorna el payload si es válido, None en caso contrario.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # El token ha expirado
    except jwt.InvalidTokenError:
        return None  # El token es inválido
