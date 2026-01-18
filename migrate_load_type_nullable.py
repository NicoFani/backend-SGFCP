"""
Migración: Hacer load_type_id nullable en la tabla trip
"""
import shutil
from datetime import datetime
from app import create_app
from app.models.base import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("MIGRACIÓN: Hacer load_type_id nullable en trip")
    print("="*80 + "\n")
    
    # Crear backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'sgfcp.db.backup.{timestamp}'
    shutil.copy('sgfcp.db', backup_file)
    print(f"✓ Backup creado: {backup_file}\n")
    
    try:
        # SQLite no permite ALTER COLUMN directamente, necesitamos recrear la tabla
        print("Recreando tabla trip con load_type_id nullable...")
        
        # 1. Crear tabla temporal con la nueva estructura
        db.session.execute(text("""
            CREATE TABLE trip_new (
                id INTEGER PRIMARY KEY,
                origin VARCHAR(100) NOT NULL,
                origin_description VARCHAR(255),
                destination VARCHAR(100) NOT NULL,
                destination_description VARCHAR(255),
                document_type VARCHAR(10),
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
                load_type_id INTEGER,
                driver_id INTEGER NOT NULL,
                FOREIGN KEY (client_id) REFERENCES client(id),
                FOREIGN KEY (load_owner_id) REFERENCES load_owner(id),
                FOREIGN KEY (load_type_id) REFERENCES load_type(id),
                FOREIGN KEY (driver_id) REFERENCES driver(id)
            )
        """))
        
        # 2. Copiar datos de la tabla antigua a la nueva
        db.session.execute(text("""
            INSERT INTO trip_new 
            SELECT * FROM trip
        """))
        
        # 3. Eliminar tabla antigua
        db.session.execute(text("DROP TABLE trip"))
        
        # 4. Renombrar tabla nueva
        db.session.execute(text("ALTER TABLE trip_new RENAME TO trip"))
        
        db.session.commit()
        print("✓ Tabla trip recreada con load_type_id nullable\n")
        
        print("="*80)
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80 + "\n")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ ERROR durante la migración: {str(e)}")
        print(f"✓ Puedes restaurar desde el backup: {backup_file}\n")
        raise
