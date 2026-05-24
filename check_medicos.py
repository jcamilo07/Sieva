import psycopg2

def check_db(name):
    print(f"\n===== {name} =====")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database=name,
            user="postgres",
            password="123456"
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nombre, email FROM medico_experto;")
        rows = cursor.fetchall()
        print("medico_experto rows:")
        for r in rows:
            print(f"  id:{r[0]}, nombre:{r[1]}, email:{r[2]}")
            
        cursor.execute("SELECT id, nombre, email FROM usuarios;")
        rows_u = cursor.fetchall()
        print("\nusuarios rows:")
        for r in rows_u:
            print(f"  id:{r[0]}, nombre:{r[1]}, email:{r[2]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_db("MedIA")
check_db("Sieva")
