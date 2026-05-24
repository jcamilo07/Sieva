import psycopg2

try:
    conn = psycopg2.connect('host=localhost port=5432 dbname=MedIA user=postgres password=123456')
    cur = conn.cursor()
    
    # Seleccionar antes de limpiar
    cur.execute("SELECT id, email, password_hash FROM usuarios")
    print("Antes de limpiar:")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Email: {row[1]}, Hash (repr): {repr(row[2])}")
        
    # Limpiar saltos de línea y espacios
    cur.execute("UPDATE usuarios SET password_hash = REGEXP_REPLACE(password_hash, '[\r\n\\s]+', '', 'g')")
    conn.commit()
    print(f"\nFilas actualizadas: {cur.rowcount}")
    
    # Seleccionar después de limpiar
    cur.execute("SELECT id, email, password_hash FROM usuarios")
    print("\nDespués de limpiar:")
    for row in cur.fetchall():
        print(f"ID: {row[0]}, Email: {row[1]}, Hash (repr): {repr(row[2])}")
        
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
