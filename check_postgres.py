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
    
    # Query all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print("\nPostgreSQL Tables in Sieva:")
    for t in tables:
        print(f"- {t}")
        
    print("\nTable Details in Sieva:")
    for t in tables:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (t,))
        cols = cursor.fetchall()
        print(f"\nTable '{t}':")
        for col in cols:
            print(f"  {col[0]} ({col[1]})")
            
    conn.close()
except Exception as e:
    print(f"Error querying Sieva: {e}")
