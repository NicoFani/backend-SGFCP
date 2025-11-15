"""
Script para inicializar la base de datos SQLite
Crea todas las tablas definidas en los modelos
"""
from app import create_app
from app.db import db

def init_database():
    """Inicializa la base de datos y crea todas las tablas"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creando tablas en la base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        
        print("✅ Base de datos inicializada correctamente")
        print(f"📁 Archivo de base de datos: sgfcp.db")
        print("\nTablas creadas:")
        
        # Listar todas las tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f"  - {table_name}")

if __name__ == "__main__":
    init_database()
