import sqlite3

conn = sqlite3.connect('sgfcp.db')
c = conn.cursor()

c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [t[0] for t in c.fetchall()]
print("Tablas disponibles:", tables)

conn.close()
