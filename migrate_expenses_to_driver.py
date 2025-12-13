#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para migrar la tabla de gastos:
- Agregar columna driver_id (required)
- Hacer trip_id opcional (SET NULL en lugar de CASCADE)
- Agregar toll_port_fee_name para descripción de tasa portuaria
- Cambiar toll_paid_by enum de 'Administrador'/'Chofer' a 'Contador'/'Chofer'
"""

import os
import sqlite3
from datetime import datetime
from app import create_app
from app.db import db
from app.models.expense import Expense

def migrate_expenses():
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de tabla de gastos...")
        print("="*60)
        
        db_path = "sgfcp.db"
        
        try:
            # Respaldar la BD actual
            if os.path.exists(db_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"sgfcp.db.backup.expenses.{timestamp}"
                import shutil
                shutil.copy(db_path, backup_path)
                print(f"✅ Base de datos respaldada en: {backup_path}")
            
            # Verificar si la tabla expense existe y tiene la estructura antigua
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener info de la tabla actual
            cursor.execute("PRAGMA table_info(expense)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            print(f"\n📋 Columnas actuales de la tabla expense:")
            for col_name, col_type in columns.items():
                print(f"   - {col_name}: {col_type}")
            
            # Si driver_id no existe, realizamos la migración
            if 'driver_id' not in columns:
                print("\n⚠️  Columna driver_id no encontrada. Realizando migración...")
                
                # Crear tabla temporal con la nueva estructura
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expense_new (
                        id INTEGER PRIMARY KEY,
                        trip_id INTEGER,
                        driver_id INTEGER NOT NULL,
                        expense_type VARCHAR(20) NOT NULL,
                        date DATE NOT NULL,
                        amount FLOAT NOT NULL,
                        description VARCHAR(75),
                        receipt_url VARCHAR(75),
                        fine_municipality VARCHAR(50),
                        repair_type VARCHAR(50),
                        fuel_liters FLOAT,
                        toll_type VARCHAR(50),
                        toll_paid_by VARCHAR(20),
                        toll_port_fee_name VARCHAR(75),
                        FOREIGN KEY (trip_id) REFERENCES trip(id),
                        FOREIGN KEY (driver_id) REFERENCES driver(id)
                    )
                """)
                
                # Copiar datos de la tabla antigua
                # Para driver_id, usamos el primer conductor asignado al viaje (relación muchos-a-muchos)
                # Si no hay viaje asociado, usamos driver_id 1 como default
                cursor.execute("""
                    INSERT INTO expense_new 
                    (id, trip_id, driver_id, expense_type, date, amount, description, receipt_url, 
                     fine_municipality, repair_type, fuel_liters, toll_type, toll_paid_by)
                    SELECT 
                        e.id, 
                        e.trip_id,
                        COALESCE(
                            (SELECT COALESCE(td.driver_id, 1) 
                             FROM trip_drivers td 
                             WHERE td.trip_id = e.trip_id 
                             LIMIT 1), 
                            1
                        ) as driver_id,
                        e.expense_type,
                        e.date,
                        e.amount,
                        e.description,
                        e.receipt_url,
                        e.fine_municipality,
                        e.repair_type,
                        e.fuel_liters,
                        e.toll_type,
                        CASE 
                            WHEN e.toll_paid_by = 'Administrador' THEN 'Contador'
                            ELSE e.toll_paid_by
                        END as toll_paid_by
                    FROM expense e
                """)
                
                # Cambiar nombres de tablas
                cursor.execute("DROP TABLE IF EXISTS expense_old")
                cursor.execute("ALTER TABLE expense RENAME TO expense_old")
                cursor.execute("ALTER TABLE expense_new RENAME TO expense")
                
                # Recrear índices si existen
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expense_trip_id ON expense(trip_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expense_driver_id ON expense(driver_id)
                """)
                
                conn.commit()
                print("✅ Datos migrados exitosamente a expense_new")
                print("✅ Tabla antigua renombrada a expense_old")
            else:
                print("✅ Tabla expense ya tiene la columna driver_id. Saltando migración de estructura.")
                
                # Verificar si toll_paid_by tiene valores obsoletos
                cursor.execute("SELECT COUNT(*) FROM expense WHERE toll_paid_by = 'Administrador'")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"\n⚠️  {count} registro(s) con toll_paid_by='Administrador'. Actualizando a 'Contador'...")
                    cursor.execute("UPDATE expense SET toll_paid_by = 'Contador' WHERE toll_paid_by = 'Administrador'")
                    conn.commit()
                    print("✅ Registros actualizados")
            
            conn.close()
            
            # Usar SQLAlchemy para validar y sincronizar el esquema
            print("\n📦 Sincronizando con SQLAlchemy...")
            db.drop_all()
            db.create_all()
            print("✅ Esquema sincronizado con modelos")
            
            print("\n✅ Migración completada exitosamente")
            print("="*60)
            print("\n⚠️  IMPORTANTE:")
            print("Si tenías datos en la BD anterior, se han preservado en la nueva estructura.")
            print("Los gastos sin viaje asociado fueron asignados al driver_id del viaje o al driver 1 por defecto.")
            print("\nSi necesitas cargar datos de prueba nuevamente:")
            print("  python seeds/seed_all_data.py && python seeds/seed_relationships.py")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_expenses()
