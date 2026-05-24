"""Paquete *services*.

Contiene la factoría para instanciar el servicio de datos. En esta
versión el frontend depende exclusivamente del backend PostgreSQL apuntado
por `config.API_BASE_URL`.
"""

from .api_service import ApiService


def create_service():
    """Devuelve el servicio HTTP que consumirá la API.

    No hay respaldo local: si la API remota no se encuentra las operaciones
    CRUD fallarán con un error de conexión visible en los logs.
    """
    return ApiService()
