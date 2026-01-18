"""
Script para migrar la relación Trip-Driver de muchos-a-muchos a uno-a-uno:
1. Eliminar todos los viajes existentes
2. Eliminar tabla intermedia trip_drivers
3. Agregar campo driver_id a tabla trip
"""

import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.db import db
from sqlalchemy import text

def backup_database():
    """Crear backup de la base de datos antes de la migración"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"sgfcp.db.backup.{timestamp}"
    
    import shutil
    if os.path.exists('sgfcp.db'):
        shutil.copy2('sgfcp.db', backup_file)
        print(f"✓ Backup creado: {backup_file}")
        return True
    return False

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("\n=== MIGRACIÓN: TRIP ONE-TO-ONE DRIVER ===\n")
        
        # 1. Crear backup
        print("1. Creando backup...")
        backup_database()
        
        # 2. Eliminar todos los viajes
        print("\n2. Eliminando viajes existentes...")
        try:
            # Primero eliminar registros de la tabla intermedia trip_drivers
            db.session.execute(text("DELETE FROM trip_drivers"))
            
            # Luego eliminar expenses asociados a trips
            db.session.execute(text("DELETE FROM expense WHERE trip_id IS NOT NULL"))
            
            # Finalmente eliminar trips
            db.session.execute(text("DELETE FROM trip"))
            db.session.commit()
            print("✓ Viajes eliminados")
        except Exception as e:
            print(f"✗ Error eliminando viajes: {e}")
            db.session.rollback()
            return False
        
        # 3. Recrear tabla trip con driver_id
        print("\n3. Modificando estructura de tabla trip...")
        try:
            # Crear tabla temporal con la nueva estructura
            db.session.execute(text("""
                CREATE TABLE trip_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    origin VARCHAR(100) NOT NULL,
                    origin_description VARCHAR(255),
                    destination VARCHAR(100) NOT NULL,
                    destination_description VARCHAR(255),
                    document_type VARCHAR(20),
                    document_number VARCHAR(20),
                    estimated_kms FLOAT,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    load_weight_on_load FLOAT,
                    load_weight_on_unload FLOAT,
                    calculated_per_km BOOLEAN NOT NULL DEFAULT 0,
                    rate FLOAT,
                    fuel_on_client BOOLEAN DEFAULT 0,
                    fuel_liters FLOAT,
                    state_id VARCHAR(20) NOT NULL,
                    client_id INTEGER NOT NULL,
                    load_owner_id INTEGER,
                    load_type_id INTEGER NOT NULL,
                    driver_id INTEGER NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES client(id),
                    FOREIGN KEY (load_owner_id) REFERENCES load_owner(id),
                    FOREIGN KEY (load_type_id) REFERENCES load_type(id),
                    FOREIGN KEY (driver_id) REFERENCES driver(id)
                )
            """))
            
            # Eliminar tabla antigua
            db.session.execute(text("DROP TABLE IF EXISTS trip"))
            
            # Renombrar tabla nueva
            db.session.execute(text("ALTER TABLE trip_new RENAME TO trip"))
            
            db.session.commit()
            print("✓ Tabla trip actualizada con driver_id")
        except Exception as e:
            print(f"✗ Error modificando trip: {e}")
            db.session.rollback()
            return False
        
        # 4. Eliminar tabla trip_drivers
        print("\n4. Eliminando tabla intermedia trip_drivers...")
        try:
            db.session.execute(text("DROP TABLE IF EXISTS trip_drivers"))
            db.session.commit()
            print("✓ Tabla trip_drivers eliminada")
        except Exception as e:
            print(f"✗ Error eliminando trip_drivers: {e}")
            db.session.rollback()
            return False
        
        print("\n=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===")
        print("Cambios realizados:")
        print("  - Relación Trip-Driver cambiada de many-to-many a one-to-one")
        print("  - Campo driver_id agregado a tabla trip")
        print("  - Tabla intermedia trip_drivers eliminada")
        print("\nAhora al crear viajes con múltiples choferes,")
        print("se crearán múltiples viajes independientes (uno por chofer)\n")
        return True

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
