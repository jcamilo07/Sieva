import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="Sieva",
        user="postgres",
        password="123456"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, descripcion FROM criterios_evaluacion;")
    rows = cursor.fetchall()
    print("criterios_evaluacion in Sieva:")
    for r in rows:
        print(f"  id:{r[0]}, nombre:{r[1]}, descripcion:{r[2]}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
