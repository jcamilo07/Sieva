"""
diagnostico_puntajes.py - Script temporal para verificar puntajes_casos con token JWT.
"""
import requests
import sqlite3
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5034")
DB_PATH = "data.db"

# Generar token maestro igual al que usa auth_service.py
secret = "MySuperSecretKey1234567890!@#$%^&*()_+"
payload = {
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "admin_maestro@sieva.com",
    "tabla": "usuarios",
    "campoUsuario": "email",
    "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    "iss": "MyApp",
    "aud": "MyAppUsers"
}
token = jwt.encode(payload, secret, algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

print("=" * 60)
print(f"API: {API_BASE_URL}")
print("=" * 60)

# 1. Consultar puntajes_casos
print("\n[1] Consultando puntajes_casos desde la API REST (con JWT)...")
try:
    r = requests.get(f"{API_BASE_URL}/api/puntajes_casos", headers=headers)
    print(f"    Status: {r.status_code}")
    if r.ok:
        datos = r.json()
        registros = datos.get("datos", [])
        print(f"    Total registros en puntajes_casos: {len(registros)}")
        if registros:
            print(f"    Primeros 5 registros:")
            for p in registros[:5]:
                print(f"      -> caso_id={p.get('caso_id')}, puntaje={p.get('puntaje')}, medico_id={p.get('medico_experto_id')}, id={p.get('id')}")
        else:
            print("    ADVERTENCIA: La tabla puntajes_casos esta VACIA.")
    else:
        print(f"    ERROR HTTP {r.status_code}: {r.text[:200]}")
except Exception as ex:
    print(f"    ERROR: {ex}")

# 2. Consultar local SQLite
print("\n[2] Consultando local_casos_clinicos desde SQLite...")
try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM local_casos_clinicos WHERE calificacion_ia IS NOT NULL AND calificacion_ia > 0")
    filas = c.fetchall()
    conn.close()
    print(f"    Total con calificacion en SQLite: {len(filas)}")
    if filas:
        for f in list(filas)[:5]:
            print(f"      -> id={f['id']}, cal={f['calificacion_ia']}")
    else:
        print("    ADVERTENCIA: El SQLite local no tiene calificaciones.")
except Exception as ex:
    print(f"    ERROR SQLite: {ex}")

# 3. Verificar casos_clinicos
print("\n[3] Verificando casos_clinicos...")
try:
    r2 = requests.get(f"{API_BASE_URL}/api/casos_clinicos", headers=headers)
    datos2 = r2.json()
    casos = datos2.get("datos", [])
    print(f"    Total casos_clinicos: {len(casos)}")
except Exception as ex:
    print(f"    ERROR: {ex}")

# 4. Verificar medico_experto
print("\n[4] Verificando medico_experto...")
try:
    r3 = requests.get(f"{API_BASE_URL}/api/medico_experto", headers=headers)
    datos3 = r3.json()
    medicos = datos3.get("datos", [])
    print(f"    Total medicos: {len(medicos)}")
    for m in medicos:
        print(f"      -> id={m.get('id')}, nombre={m.get('nombre')}, email={m.get('email')}")
except Exception as ex:
    print(f"    ERROR: {ex}")

print("\n" + "=" * 60)
print("Diagnostico completado.")
