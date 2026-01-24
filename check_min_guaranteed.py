import sqlite3

conn = sqlite3.connect('sgfcp.db')
cursor = conn.cursor()

print("Intentando contar minimum_guaranteed_history...")
cursor.execute('SELECT COUNT(*) FROM minimum_guaranteed_history')
count = cursor.fetchone()[0]
print(f"minimum_guaranteed_history: {count} registros")

conn.close()
print("FIN")
