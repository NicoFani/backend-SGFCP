import sqlite3
import os

# Configuración
DB_FILENAME = 'sgfcp.db'
OUTPUT_FILE = 'schema.sql'

def export_schema():
    # 1. VERIFICACIÓN DE RUTA
    # Obtenemos la ruta absoluta del archivo db basándonos en dónde está este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, DB_FILENAME)

    print(f"🔍 Buscando base de datos en: {db_path}")

    if not os.path.exists(db_path):
        print(f"❌ ERROR FATAL: No encuentro el archivo '{DB_FILENAME}'.")
        print("   Asegúrate de que este script.py y el archivo .db estén en la MISMA carpeta.")
        return

    # 2. CONEXIÓN
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3. EXTRACCIÓN
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        if len(tables) == 0:
            print("⚠️ ALERTA: Me conecté al archivo, pero NO tiene tablas. ¿Está vacía la base de datos?")
            conn.close()
            return

        print(f"✅ Encontré {len(tables)} tablas. Generando archivo...")

        # 4. GUARDADO
        output_path = os.path.join(current_dir, OUTPUT_FILE)
        with open(output_path, 'w', encoding='utf-8') as f:
            for name, sql in tables:
                if sql:
                    f.write(f"-- Tabla: {name}\n")
                    f.write(sql + ";\n\n")
        
        conn.close()
        print(f"🎉 ¡LISTO! Esquema guardado en: {output_path}")
        print("   -> Ahora puedes importar este archivo en Vuerd.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    export_schema()