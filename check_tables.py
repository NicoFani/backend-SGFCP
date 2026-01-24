import sqlite3

conn = sqlite3.connect('sgfcp.db')
cursor = conn.cursor()

print("=== TABLAS EN LA BASE DE DATOS ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"  - {table}")

print("\n=== CONTEO DE REGISTROS ===")
try:
    if 'driver_commission_history' in tables:
        cursor.execute('SELECT COUNT(*) FROM driver_commission_history')
        print(f"driver_commission_history: {cursor.fetchone()[0]} registros")
    else:
        print("driver_commission_history: NO EXISTE")
except Exception as e:
    print(f"driver_commission_history: ERROR - {e}")

try:
    if 'minimum_guaranteed_history' in tables:
        cursor.execute('SELECT COUNT(*) FROM minimum_guaranteed_history')
        print(f"minimum_guaranteed_history: {cursor.fetchone()[0]} registros")
    else:
        print("minimum_guaranteed_history: NO EXISTE")
except Exception as e:
    print(f"minimum_guaranteed_history: ERROR - {e}")

conn.close()
