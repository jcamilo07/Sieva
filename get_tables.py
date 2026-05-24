import sqlite3
import json

c = sqlite3.connect('data.db')
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()

schema = {}
for table in tables:
    table_name = table[0]
    columns = c.execute(f"PRAGMA table_info({table_name})").fetchall()
    schema[table_name] = [col[1] for col in columns]

with open('full_schema.json', 'w') as f:
    json.dump(schema, f, indent=4)
