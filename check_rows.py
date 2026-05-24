import psycopg2

def inspect_db(db_name):
    print(f"\n===== Inspecting Database: {db_name} =====")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database=db_name,
            user="postgres",
            password="123456"
        )
        cursor = conn.cursor()
        
        # Count cases
        cursor.execute("SELECT COUNT(*) FROM casos_clinicos;")
        cases_count = cursor.fetchone()[0]
        print(f"casos_clinicos rows: {cases_count}")
        
        # Show first 3 cases if any
        if cases_count > 0:
            cursor.execute("SELECT id, id_caso, nivel_dificultad, modelo_id, observacion FROM casos_clinicos ORDER BY id LIMIT 3;")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  Case row -> id:{r[0]}, id_caso:{r[1]}, diff:{r[2]}, model:{r[3]}, obs:{r[4]}")
                
        # Count scores
        try:
            cursor.execute("SELECT COUNT(*) FROM puntajes_casos;")
            scores_count = cursor.fetchone()[0]
            print(f"puntajes_casos rows: {scores_count}")
            if scores_count > 0:
                cursor.execute("SELECT id, caso_id, puntaje FROM puntajes_casos LIMIT 3;")
                rows = cursor.fetchall()
                for r in rows:
                    print(f"  Score row -> id:{r[0]}, caso_id:{r[1]}, puntaje:{r[2]}")
        except Exception as e:
            print(f"puntajes_casos: Table or query failed: {e}")
            
        try:
            cursor.execute("SELECT COUNT(*) FROM puntajes_casos;")
            scores_count = cursor.fetchone()[0]
            print(f"puntajes_casos rows: {scores_count}")
        except Exception as e:
            print(f"puntajes_casos: Table or query failed: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to database {db_name}: {e}")

inspect_db("MedIA")
inspect_db("Sieva")
