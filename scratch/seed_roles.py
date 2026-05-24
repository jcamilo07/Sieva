import psycopg2

try:
    conn = psycopg2.connect('host=localhost port=5432 dbname=MedIA user=postgres password=123456')
    cur = conn.cursor()
    
    # Insertar roles
    roles_a_insertar = [
        (1, 'Administrador', 'Administrador general del sistema con acceso total'),
        (2, 'Medico', 'Médico usuario con acceso a casos clínicos y ejecuciones')
    ]
    
    for r_id, r_nombre, r_desc in roles_a_insertar:
        cur.execute("SELECT COUNT(*) FROM roles WHERE id = %s", (r_id,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO roles (id, nombre, descripcion) VALUES (%s, %s, %s)", (r_id, r_nombre, r_desc))
            print(f"Rol '{r_nombre}' insertado.")
        else:
            print(f"Rol '{r_nombre}' ya existe.")
            
    # Asignar rol Administrador al usuario con ID 1 (juancamiloblanquiceth10@gmail.com)
    cur.execute("SELECT COUNT(*) FROM usuario_rol WHERE usuario_id = 1 AND rol_id = 1")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (1, 1)")
        print("Rol 'Administrador' asignado al usuario 1 (juancamiloblanquiceth10@gmail.com).")
    else:
        print("El usuario ya tiene asignado el rol 'Administrador'.")
        
    conn.commit()
    cur.close()
    conn.close()
    print("Base de datos actualizada con éxito.")
except Exception as e:
    print("Error:", e)
