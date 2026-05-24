import sqlite3

c = sqlite3.connect('data.db')
columns = [col[1] for col in c.execute('PRAGMA table_info(casos_clinicos)').fetchall()]

with open('schema.txt', 'w') as f:
    for col in columns:
        f.write(col + '\n')
