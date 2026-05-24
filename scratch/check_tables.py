import psycopg2

try:
    conn = psycopg2.connect('host=localhost port=5432 dbname=MedIA user=postgres password=123456')
    cur = conn.cursor()
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = [r[0] for r in cur.fetchall()]
    print("Tablas encontradas:")
    for t in tables:
        try:
            cur.execute(f'SELECT count(*) FROM "{t}"')
            cnt = cur.fetchone()[0]
            print(f"  - {t}: {cnt} registros")
        except Exception as te:
            print(f"  - {t}: Error al contar ({te})")
            conn.rollback()
            
    cur.close()
    conn.close()
except Exception as e:
    print("Error general:", e)
