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
    
    cursor.execute("""
        SELECT column_name, is_nullable, column_default, data_type
        FROM information_schema.columns
        WHERE table_name = 'puntajes_casos' AND table_schema = 'public'
        ORDER BY ordinal_position;
    """)
    rows = cursor.fetchall()
    print("Columns nullability in 'puntajes_casos':")
    for r in rows:
        print(f"  {r[0]}: Nullable={r[1]}, Default={r[2]}, Type={r[3]}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
