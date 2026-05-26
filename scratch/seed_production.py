"""
seed_production.py
Configura usuarios, roles y médico experto para producción.
Las contraseñas NUNCA se guardan en texto plano - siempre bcrypt.
"""
import psycopg2
import bcrypt

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="Sieva", user="postgres", password="123456"
    )
    cursor = conn.cursor()

    # ─── 1. LIMPIAR DATOS DE PRUEBA ───────────────────────────────────────────

    print("Limpiando usuario_rol de usuarios de prueba...")
    cursor.execute("DELETE FROM usuario_rol WHERE usuario_id IN (1, 2)")

    print("Eliminando usuarios de prueba (Juan Blanquiceth, Juan Lujan)...")
    cursor.execute("DELETE FROM usuarios WHERE id IN (1, 2)")

    print("Limpiando tabla medico_experto (datos de prueba)...")
    cursor.execute("DELETE FROM medico_experto")

    # Resetear secuencias para IDs limpios
    cursor.execute("ALTER SEQUENCE usuarios_id_seq RESTART WITH 1")
    cursor.execute("ALTER SEQUENCE medico_experto_id_seq RESTART WITH 1")

    # ─── 2. INSERTAR USUARIOS DE PRODUCCIÓN ──────────────────────────────────

    usuarios = [
        {
            "nombre": "Carlos Manuel Castro Londoño",
            "email":  "cmanuel.castro@udea.edu.co",
            "password": "@Manuel876",
            "activo": True,
            "rol_nombre": "Medico"
        },
        {
            "nombre": "Carlos Arturo Castro",
            "email":  "carlos.castro@usbmed.edu.co",
            "password": "@Ccastro441",
            "activo": True,
            "rol_nombre": "Administrador"
        }
    ]

    for u in usuarios:
        pw_hash = hash_password(u["password"])

        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password_hash, activo)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (u["nombre"], u["email"], pw_hash, u["activo"]))
        new_id = cursor.fetchone()[0]

        # Obtener id del rol
        cursor.execute("SELECT id FROM roles WHERE nombre = %s", (u["rol_nombre"],))
        rol_row = cursor.fetchone()
        if not rol_row:
            print(f"  [ERROR] Rol '{u['rol_nombre']}' no encontrado!")
            continue
        rol_id = rol_row[0]

        cursor.execute("""
            INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)
        """, (new_id, rol_id))

        print(f"  ✓ Usuario '{u['nombre']}' creado con ID={new_id}, rol='{u['rol_nombre']}'")

    # ─── 3. INSERTAR MÉDICO EXPERTO DE PRODUCCIÓN ─────────────────────────────

    cursor.execute("""
        INSERT INTO medico_experto (nombre, email)
        VALUES (%s, %s)
    """, ("Carlos Manuel Castro Londoño", "cmanuel.castro@udea.edu.co"))
    print("  ✓ Médico experto registrado en tabla medico_experto")

    # ─── 4. VERIFICACIÓN FINAL ────────────────────────────────────────────────

    print("\n=== VERIFICACIÓN FINAL ===")

    print("\n[usuarios]")
    cursor.execute("SELECT id, nombre, email, activo FROM usuarios ORDER BY id")
    for r in cursor.fetchall():
        print(f"  ID:{r[0]} | {r[1]} | {r[2]} | activo={r[3]}")

    print("\n[usuario_rol]")
    cursor.execute("""
        SELECT u.nombre, r.nombre
        FROM usuario_rol ur
        JOIN usuarios u ON u.id = ur.usuario_id
        JOIN roles r ON r.id = ur.rol_id
        ORDER BY u.id
    """)
    for r in cursor.fetchall():
        print(f"  {r[0]} → Rol: {r[1]}")

    print("\n[medico_experto]")
    cursor.execute("SELECT id, nombre, email FROM medico_experto ORDER BY id")
    for r in cursor.fetchall():
        print(f"  ID:{r[0]} | {r[1]} | {r[2]}")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n✅ Proceso completado y guardado en PostgreSQL.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback; traceback.print_exc()
