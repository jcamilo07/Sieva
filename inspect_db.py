import sqlite3

conn = sqlite3.connect('data.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Tablas completas
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [r[0] for r in c.fetchall()]
print('TODAS LAS TABLAS:', tablas)

# Revisar si hay tablas de ejecuciones/puntajes
for tabla in tablas:
    try:
        c.execute(f'SELECT COUNT(*) FROM {tabla}')
        cnt = c.fetchone()[0]
        c.execute(f'PRAGMA table_info({tabla})')
        cols = [r[1] for r in c.fetchall()]
        print(f'\nTABLA [{tabla}] - {cnt} registros')
        print(f'  Columnas: {cols}')
        if cnt > 0 and cnt <= 5:
            c.execute(f'SELECT * FROM {tabla}')
            for r in c.fetchall():
                d = dict(r)
                # Truncate long strings
                for k,v in d.items():
                    if isinstance(v, str) and len(v) > 80:
                        d[k] = v[:80] + '...'
                print(f'  ROW: {d}')
    except Exception as e:
        print(f'Error en {tabla}: {e}')

conn.close()
