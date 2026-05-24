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
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'puntajes_casos';
    """)
    rows = cursor.fetchall()
    print("Foreign Keys in 'puntajes_casos':")
    for r in rows:
        print(f"  {r[1]} -> {r[2]}({r[3]})")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
