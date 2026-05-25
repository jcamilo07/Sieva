import sys, os
sys.path.append(os.getcwd())
from app import app
from services import create_service
with app.app_context():
    api = create_service()
    casos = api.listar('casos_clinicos')
    if casos:
        print(casos[0].keys())
