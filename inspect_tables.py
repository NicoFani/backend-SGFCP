"""
Script para inspeccionar la estructura actual de las tablas antes de migrar.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def inspect_table(table_name):
    """Inspeccionar la estructura de una tabla."""
    print(f"\nTabla: {table_name}")
    print("-" * 60)
    
    result = db.session.execute(text(f"""
        PRAGMA table_info({table_name})
    """))
    
    columns = result.fetchall()
    if columns:
        print(f"{'#':<5} {'Nombre':<30} {'Tipo':<15} {'Not Null':<10} {'Default'}")
        print("-" * 60)
        for col in columns:
            cid, name, dtype, notnull, default_val, pk = col
            print(f"{cid:<5} {name:<30} {dtype:<15} {notnull:<10} {default_val}")
    else:
        print("Tabla no encontrada")

def run_inspection():
    """Inspeccionar todas las tablas relevantes."""
    print("=" * 60)
    print("INSPECCIÓN DE ESTRUCTURA DE TABLAS")
    print("=" * 60)
    
    tables = ['expense', 'driver', 'payroll_periods', 'payroll_summaries']
    
    for table in tables:
        inspect_table(table)
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        run_inspection()
