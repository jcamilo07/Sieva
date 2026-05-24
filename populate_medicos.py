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
    
    # We want to make sure Juan Blanquiceth and Juan Lujan are in there
    medicos = [
        (1, "Juan Blanquiceth", "juancamiloblanquiceth10@gmail.com"),
        (2, "Juan Lujan", "jpablolujanborraez@gmail.com"),
        (3, "hugo", "hugo@medico.com"),
        (4, "paco", "paco@medico.com"),
        (5, "luís", "luis@medico.com")
    ]
    
    for m_id, name, email in medicos:
        cursor.execute("SELECT id FROM medico_experto WHERE email = %s;", (email,))
        row = cursor.fetchone()
        if not row:
            print(f"Inserting {name}...")
            cursor.execute(
                "INSERT INTO medico_experto (id, nombre, email) OVERRIDING SYSTEM VALUE VALUES (%s, %s, %s);",
                (m_id, name, email)
            )
        else:
            print(f"{name} already exists.")
            
    # Sync serial/identity sequence
    cursor.execute("""
        SELECT setval(
            pg_get_serial_sequence('medico_experto', 'id'), 
            coalesce(max(id), 1)
        ) FROM medico_experto;
    """)
    
    conn.commit()
    print("Done populating!")
    
    cursor.execute("SELECT id, nombre, email FROM medico_experto;")
    print("\nCurrent medico_experto rows:")
    for r in cursor.fetchall():
        print(f"  id:{r[0]}, nombre:{r[1]}, email:{r[2]}")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
