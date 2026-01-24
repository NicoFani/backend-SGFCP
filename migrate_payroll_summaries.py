"""Script para ejecutar la migración de payroll_summaries"""
import sys
import os

# Agregar la carpeta raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate():
    """Ejecutar la migración para agregar is_auto_generated a payroll_summaries"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Iniciando migración...")
            print("Agregando columna 'is_auto_generated' a 'payroll_summaries'...")
            
            # Ejecutar la migración
            db.session.execute(text(
                "ALTER TABLE payroll_summaries ADD COLUMN is_auto_generated BOOLEAN DEFAULT FALSE"
            ))
            db.session.commit()
            
            print("✓ Migración completada exitosamente!")
            print("✓ Columna 'is_auto_generated' agregada con valor por defecto FALSE")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error en la migración: {str(e)}")
            
            # Si es porque la columna ya existe, es OK
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("⚠ La columna ya existe. No es necesario hacer nada.")
                return 0
            else:
                print("Por favor, verifica tu conexión a la BD y intenta de nuevo.")
                return 1

if __name__ == "__main__":
    exit_code = migrate()
    sys.exit(exit_code)
