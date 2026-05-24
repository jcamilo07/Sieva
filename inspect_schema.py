import json

with open('full_db_schema.json', 'r', encoding='utf-16') as f:
    schema = json.load(f)

for table in schema.get('tablas', []):
    cols = [col.get('column_name') for col in table.get('columnas', [])]
    if 'medico_experto_id' in cols or 'puntaje' in cols:
        print(f"Table: {table.get('table_name')}")
        print(f"Columns: {cols}")
        print("-" * 40)
