"""
Script para migrar la base de datos:
1. Eliminar todos los viajes existentes
2. Eliminar columnas antiguas de Trip: rate_per_ton, km_rate, calculation_type
3. Agregar nuevas columnas a Trip: calculated_per_km, rate, load_type_id
4. Crear tabla LoadType
5. Poblar LoadType con datos iniciales
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
        print("\n=== INICIANDO MIGRACIÓN DE BASE DE DATOS ===\n")
        
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
            result = db.session.execute(text("DELETE FROM trip"))
            db.session.commit()
            print(f"✓ Viajes eliminados")
        except Exception as e:
            print(f"✗ Error eliminando viajes: {e}")
            db.session.rollback()
            return False
        
        # 3. Crear tabla load_type
        print("\n3. Creando tabla load_type...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS load_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    default_calculated_per_km BOOLEAN NOT NULL DEFAULT 0
                )
            """))
            db.session.commit()
            print("✓ Tabla load_type creada")
        except Exception as e:
            print(f"✗ Error creando tabla load_type: {e}")
            db.session.rollback()
            return False
        
        # 4. Poblar tabla load_type
        print("\n4. Poblando tabla load_type con datos iniciales...")
        try:
            # Tipos por tonelada (default_calculated_per_km = False)
            tonnage_types = ['Girasol', 'Maíz', 'Soja', 'Trigo', 'Cebada', 'Pellets', 'Sorgo', 'Espiga']
            for name in tonnage_types:
                db.session.execute(text(
                    "INSERT OR IGNORE INTO load_type (name, default_calculated_per_km) VALUES (:name, 0)"
                ), {'name': name})
            
            # Tipos por km (default_calculated_per_km = True)
            km_types = ['Bolsones para reparto', 'Semillas']
            for name in km_types:
                db.session.execute(text(
                    "INSERT OR IGNORE INTO load_type (name, default_calculated_per_km) VALUES (:name, 1)"
                ), {'name': name})
            
            db.session.commit()
            print(f"✓ {len(tonnage_types)} tipos por tonelada agregados")
            print(f"✓ {len(km_types)} tipos por km agregados")
        except Exception as e:
            print(f"✗ Error poblando load_type: {e}")
            db.session.rollback()
            return False
        
        # 5. Modificar tabla trip - crear nueva tabla temporal
        print("\n5. Modificando estructura de tabla trip...")
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
                    FOREIGN KEY (client_id) REFERENCES client(id),
                    FOREIGN KEY (load_owner_id) REFERENCES load_owner(id),
                    FOREIGN KEY (load_type_id) REFERENCES load_type(id)
                )
            """))
            
            # Eliminar tabla antigua
            db.session.execute(text("DROP TABLE IF EXISTS trip"))
            
            # Renombrar tabla nueva
            db.session.execute(text("ALTER TABLE trip_new RENAME TO trip"))
            
            db.session.commit()
            print("✓ Estructura de trip actualizada")
            print("  - Eliminados: rate_per_ton, km_rate, calculation_type")
            print("  - Agregados: calculated_per_km, rate, load_type_id")
        except Exception as e:
            print(f"✗ Error modificando trip: {e}")
            db.session.rollback()
            return False
        
        print("\n=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===\n")
        return True

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
