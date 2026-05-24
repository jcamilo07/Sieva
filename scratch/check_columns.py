import psycopg2

try:
    conn = psycopg2.connect('host=localhost port=5432 dbname=MedIA user=postgres password=123456')
    cur = conn.cursor()
    
    for t in ['roles', 'usuario_rol', 'usuarios']:
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{t}'")
        print(f"Columnas de {t}:")
        for col in cur.fetchall():
            print(f"  - {col[0]} ({col[1]})")
            
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
