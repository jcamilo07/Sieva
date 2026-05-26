import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="Sieva", user="postgres", password="123456"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medico_experto ORDER BY id")
    cols = [d[0] for d in cursor.description]
    print(f"Columnas: {cols}")
    print("\n=== MEDICO_EXPERTO ===")
    for r in cursor.fetchall():
        print(dict(zip(cols, r)))

    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
