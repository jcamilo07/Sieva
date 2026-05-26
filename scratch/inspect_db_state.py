import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="Sieva", user="postgres", password="123456"
    )
    cursor = conn.cursor()

    print("=== ROLES ===")
    cursor.execute("SELECT id, nombre FROM roles ORDER BY id")
    for r in cursor.fetchall():
        print(f"  ID:{r[0]} | {r[1]}")

    print("\n=== USUARIOS ===")
    cursor.execute("SELECT id, nombre, email, activo FROM usuarios ORDER BY id")
    for r in cursor.fetchall():
        print(f"  ID:{r[0]} | {r[1]} | {r[2]} | activo={r[3]}")

    print("\n=== USUARIO_ROL ===")
    cursor.execute("SELECT usuario_id, rol_id FROM usuario_rol ORDER BY usuario_id")
    for r in cursor.fetchall():
        print(f"  usuario_id:{r[0]} -> rol_id:{r[1]}")

    print("\n=== TABLAS CON 'medic' EN SU NOMBRE ===")
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name ILIKE '%medic%'
        ORDER BY table_name
    """)
    for r in cursor.fetchall():
        print(f"  {r[0]}")

    print("\n=== TODAS LAS TABLAS ===")
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name
    """)
    for r in cursor.fetchall():
        print(f"  {r[0]}")

    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
