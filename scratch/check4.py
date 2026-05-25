import sys, os
sys.path.append(os.getcwd())
import requests
from services.auth_service import AuthService
token = AuthService()._get_admin_token()
res = requests.get('http://localhost:5034/api/casos_clinicos', headers={'Authorization': f'Bearer {token}'})
data = res.json()
if 'datos' in data and data['datos']:
    print(data['datos'][0].keys())
else:
    print("No data")
