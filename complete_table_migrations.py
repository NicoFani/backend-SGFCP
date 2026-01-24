"""
Script para completar las migraciones de tablas que requieren recreación en SQLite.

Este script:
1. Recrea tabla expense sin toll_paid_by, con paid_by_admin
2. Recrea tabla driver sin commission
3. Recrea tabla payroll_periods sin status y actual_close_date
4. Recrea tabla payroll_summaries con nuevos campos

IMPORTANTE: Ejecutar DESPUÉS de migrate_payroll_refactor.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def recreate_expense_table():
    """Recrear tabla expense sin toll_paid_by."""
    print("\n1. Recreando tabla expense...")
    
    try:
        # Verificar si paid_by_admin ya existe y toll_paid_by no
        result = db.session.execute(text("""
            PRAGMA table_info(expense)
        """))
        columns = [row[1] for row in result.fetchall()]
        
        if 'paid_by_admin' in columns and 'toll_paid_by' not in columns:
            print("   ✓ Tabla expense ya está migrada")
            return
        
        # Crear tabla temporal sin toll_paid_by
        db.session.execute(text("""
            CREATE TABLE expense_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER,
                driver_id INTEGER NOT NULL,
                expense_type VARCHAR(12) NOT NULL,
                date DATE NOT NULL,
                amount FLOAT NOT NULL,
                description VARCHAR(75),
                receipt_url VARCHAR(75),
                fine_municipality VARCHAR(50),
                repair_type VARCHAR(50),
                fuel_liters FLOAT,
                toll_type VARCHAR(36),
                paid_by_admin BOOLEAN,
                toll_port_fee_name VARCHAR(75),
                FOREIGN KEY(trip_id) REFERENCES trip(id) ON DELETE SET NULL,
                FOREIGN KEY(driver_id) REFERENCES driver(id) ON DELETE CASCADE
            )
        """))
        
        # Copiar datos
        if 'toll_paid_by' in columns:
            # Si existe toll_paid_by, convertirlo a paid_by_admin
            db.session.execute(text("""
                INSERT INTO expense_new 
                (id, trip_id, driver_id, expense_type, date, amount, description, 
                 receipt_url, fine_municipality, repair_type, fuel_liters, toll_type,
                 paid_by_admin, toll_port_fee_name)
                SELECT id, trip_id, driver_id, expense_type, date, amount, description, 
                       receipt_url, fine_municipality, repair_type, fuel_liters, toll_type,
                       CASE 
                           WHEN toll_paid_by = 'Contador' THEN 1
                           WHEN toll_paid_by = 'Chofer' THEN 0
                           ELSE paid_by_admin
                       END as paid_by_admin,
                       toll_port_fee_name
                FROM expense
            """))
        else:
            # Si no existe toll_paid_by, solo copiar
            db.session.execute(text("""
                INSERT INTO expense_new 
                SELECT id, trip_id, driver_id, expense_type, date, amount, description, 
                       receipt_url, fine_municipality, repair_type, fuel_liters, toll_type,
                       paid_by_admin, toll_port_fee_name
                FROM expense
            """))
        
        # Reemplazar tabla
        db.session.execute(text("DROP TABLE expense"))
        db.session.execute(text("ALTER TABLE expense_new RENAME TO expense"))
        
        db.session.commit()
        print("   ✓ Tabla expense recreada exitosamente")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        db.session.rollback()
        raise

def recreate_driver_table():
    """Recrear tabla driver sin commission."""
    print("\n2. Recreando tabla driver...")
    
    try:
        # Verificar si commission todavía existe
        result = db.session.execute(text("""
            PRAGMA table_info(driver)
        """))
        columns = [row[1] for row in result.fetchall()]
        
        if 'commission' not in columns:
            print("   ✓ Tabla driver ya está migrada")
            return
        
        # Crear tabla nueva sin commission (manteniendo estructura actual)
        db.session.execute(text("""
            CREATE TABLE driver_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dni INTEGER NOT NULL,
                cuil VARCHAR(11) NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                cbu VARCHAR(22) NOT NULL,
                active BOOLEAN NOT NULL,
                enrollment_date DATE NOT NULL,
                termination_date DATE,
                driver_license_due_date DATE NOT NULL,
                medical_exam_due_date DATE NOT NULL
            )
        """))
        
        # Copiar datos sin commission
        db.session.execute(text("""
            INSERT INTO driver_new 
            (id, dni, cuil, phone_number, cbu, active, enrollment_date,
             termination_date, driver_license_due_date, medical_exam_due_date)
            SELECT id, dni, cuil, phone_number, cbu, active, enrollment_date,
                   termination_date, driver_license_due_date, medical_exam_due_date
            FROM driver
        """))
        
        # Reemplazar tabla
        db.session.execute(text("DROP TABLE driver"))
        db.session.execute(text("ALTER TABLE driver_new RENAME TO driver"))
        
        db.session.commit()
        print("   ✓ Tabla driver recreada exitosamente (commission removida)")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        db.session.rollback()
        raise

def recreate_payroll_periods_table():
    """Recrear tabla payroll_periods con year, month y has_trips_in_progress."""
    print("\n3. Recreando tabla payroll_periods...")
    
    try:
        # Verificar si year y month ya existen
        result = db.session.execute(text("""
            PRAGMA table_info(payroll_periods)
        """))
        columns = [row[1] for row in result.fetchall()]
        
        if 'year' in columns and 'month' in columns and 'has_trips_in_progress' in columns:
            print("   ✓ Tabla payroll_periods ya está migrada")
            return
        
        # Crear tabla nueva con year, month, has_trips_in_progress
        db.session.execute(text("""
            CREATE TABLE payroll_periods_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                has_trips_in_progress BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Copiar datos, extrayendo year y month de start_date
        db.session.execute(text("""
            INSERT INTO payroll_periods_new 
            (id, year, month, start_date, end_date, has_trips_in_progress, created_at, updated_at)
            SELECT 
                id, 
                CAST(strftime('%Y', start_date) AS INTEGER) as year,
                CAST(strftime('%m', start_date) AS INTEGER) as month,
                start_date, 
                end_date, 
                0 as has_trips_in_progress,
                created_at, 
                COALESCE(updated_at, created_at) as updated_at
            FROM payroll_periods
        """))
        
        # Reemplazar tabla
        db.session.execute(text("DROP TABLE payroll_periods"))
        db.session.execute(text("ALTER TABLE payroll_periods_new RENAME TO payroll_periods"))
        
        db.session.commit()
        print("   ✓ Tabla payroll_periods recreada exitosamente")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        db.session.rollback()
        raise

def recreate_payroll_summaries_table():
    """Recrear tabla payroll_summaries con nuevos campos."""
    print("\n4. Recreando tabla payroll_summaries...")
    
    try:
        # Verificar estructura actual
        result = db.session.execute(text("""
            PRAGMA table_info(payroll_summaries)
        """))
        columns = [row[1] for row in result.fetchall()]
        
        # Verificar si tiene la estructura nueva
        has_new_fields = (
            'expenses_to_reimburse' in columns and 
            'expenses_to_deduct' in columns and 
            'guaranteed_minimum_applied' in columns and
            'advances_deducted' in columns and
            'total_amount' in columns
        )
        
        if has_new_fields:
            print("   ✓ Tabla payroll_summaries ya está migrada")
            return
        
        # Crear tabla nueva con la estructura actualizada
        db.session.execute(text("""
            CREATE TABLE payroll_summaries_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                driver_commission_percentage NUMERIC(5, 2) NOT NULL,
                driver_minimum_guaranteed NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
                commission_from_trips NUMERIC(12, 2) DEFAULT 0.00,
                expenses_to_reimburse NUMERIC(12, 2) DEFAULT 0.00,
                expenses_to_deduct NUMERIC(12, 2) DEFAULT 0.00,
                guaranteed_minimum_applied NUMERIC(12, 2) DEFAULT 0.00,
                advances_deducted NUMERIC(12, 2) DEFAULT 0.00,
                other_items_total NUMERIC(12, 2) DEFAULT 0.00,
                total_amount NUMERIC(12, 2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'draft',
                error_message TEXT,
                export_format VARCHAR(10),
                export_path VARCHAR(255),
                notes TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(period_id) REFERENCES payroll_periods(id),
                FOREIGN KEY(driver_id) REFERENCES driver(id)
            )
        """))
        
        # Copiar datos existentes (si los hay)
        # Mapeo de campos viejos -> nuevos:
        # total_expenses -> se divide aproximadamente en expenses_to_reimburse
        # total_advances -> advances_deducted
        # total_net -> total_amount
        # other_items_total se mantiene
        db.session.execute(text("""
            INSERT INTO payroll_summaries_new 
            (id, period_id, driver_id, driver_commission_percentage,
             driver_minimum_guaranteed, commission_from_trips, 
             expenses_to_reimburse, expenses_to_deduct,
             guaranteed_minimum_applied, advances_deducted,
             other_items_total, total_amount, status,
             error_message, export_format, export_path, notes, 
             created_at, updated_at)
            SELECT 
                id, period_id, driver_id, driver_commission_percentage,
                COALESCE(driver_minimum_guaranteed, 0.00),
                COALESCE(commission_from_trips, 0.00),
                COALESCE(total_expenses, 0.00) as expenses_to_reimburse,
                0.00 as expenses_to_deduct,
                0.00 as guaranteed_minimum_applied,
                COALESCE(total_advances, 0.00) as advances_deducted,
                COALESCE(other_items_total, 0.00),
                COALESCE(total_net, 0.00) as total_amount,
                CASE 
                    WHEN status = 'pending' THEN 'pending_approval'
                    WHEN status = 'approved' THEN 'approved'
                    WHEN status = 'calculation_pending' THEN 'calculation_pending'
                    WHEN status = 'error' THEN 'error'
                    ELSE 'draft'
                END as status,
                error_message,
                export_format, export_path, notes, 
                created_at, 
                COALESCE(updated_at, created_at) as updated_at
            FROM payroll_summaries
        """))
        
        # Reemplazar tabla
        db.session.execute(text("DROP TABLE payroll_summaries"))
        db.session.execute(text("ALTER TABLE payroll_summaries_new RENAME TO payroll_summaries"))
        
        db.session.commit()
        print("   ✓ Tabla payroll_summaries recreada exitosamente")
        print("   ℹ Campos migrados:")
        print("     - total_expenses -> expenses_to_reimburse")
        print("     - total_advances -> advances_deducted")
        print("     - total_net -> total_amount")
        print("     - Agregados: expenses_to_deduct, guaranteed_minimum_applied")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        db.session.rollback()
        raise

def run_complete_migration():
    """Ejecutar todas las migraciones de tablas."""
    print("Completando migraciones de estructura de tablas...")
    print("=" * 60)
    
    recreate_expense_table()
    recreate_driver_table()
    recreate_payroll_periods_table()
    recreate_payroll_summaries_table()
    
    print("\n" + "=" * 60)
    print("✓ Migraciones de tablas completadas exitosamente!")
    print("\nSiguientes pasos:")
    print("1. Verificar que la aplicación funcione correctamente")
    print("2. Actualizar el frontend si es necesario (ver FRONTEND_CHANGES_REQUIRED.md)")
    print("3. Probar la generación de nóminas con el nuevo sistema")

if __name__ == '__main__':
    print("ADVERTENCIA: Este script modifica la estructura de varias tablas")
    print("Asegúrate de que migrate_payroll_refactor.py ya se ejecutó correctamente")
    response = input("¿Continuar? (si/no): ")
    
    if response.lower() == 'si':
        app = create_app()
        with app.app_context():
            run_complete_migration()
    else:
        print("Migración cancelada")
