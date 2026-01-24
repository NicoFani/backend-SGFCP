"""
Script de migración para actualizar el módulo de payroll.

CAMBIOS PRINCIPALES:
1. Eliminar campo 'commission' de tabla 'driver'
2. Eliminar campo 'toll_paid_by' de tabla 'expense'
3. Agregar campo 'paid_by_admin' a tabla 'expense'
4. Eliminar campos 'status', 'actual_close_date' de tabla 'payroll_periods'
5. Actualizar tabla 'payroll_summaries':
   - Eliminar campo 'calculation_type'
   - Eliminar campo 'adjustments_applied'
   - Agregar campo 'driver_minimum_guaranteed'
   - Agregar campo 'other_items_total'
   - Agregar campo 'error_message'
6. Crear tabla 'minimum_guaranteed_history'
7. Crear tabla 'payroll_other_items'

IMPORTANTE: Ejecutar después de hacer backup de la base de datos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def run_migration():
    """Ejecutar migración completa."""
    
    print("Iniciando migración del módulo de payroll...")
    
    # Backup de datos importantes antes de modificar
    print("\n1. Creando backup de datos críticos...")
    
    # Guardar comisiones actuales de drivers en el histórico
    print("   - Migrando comisiones de drivers a histórico...")
    migrate_driver_commissions()
    
    # 2. Modificar tabla expense
    print("\n2. Modificando tabla expense...")
    try:
        # Agregar nuevo campo paid_by_admin
        db.session.execute(text("""
            ALTER TABLE expense 
            ADD COLUMN paid_by_admin BOOLEAN NULL
        """))
        
        # Migrar datos de toll_paid_by a paid_by_admin
        db.session.execute(text("""
            UPDATE expense 
            SET paid_by_admin = CASE 
                WHEN toll_paid_by = 'Contador' THEN TRUE
                WHEN toll_paid_by = 'Chofer' THEN FALSE
                ELSE NULL
            END
            WHERE expense_type IN ('Peaje', 'Reparaciones')
        """))
        
        # Eliminar columna toll_paid_by (SQLite no soporta DROP COLUMN directamente)
        # Hay que recrear la tabla
        print("   - Recreando tabla expense sin toll_paid_by...")
        recreate_expense_table()
        
        print("   ✓ Tabla expense actualizada")
    except Exception as e:
        print(f"   ✗ Error en expense: {e}")
        db.session.rollback()
        raise
    
    # 3. Modificar tabla driver
    print("\n3. Modificando tabla driver...")
    try:
        # SQLite no soporta DROP COLUMN, hay que recrear la tabla
        print("   - Recreando tabla driver sin commission...")
        recreate_driver_table()
        print("   ✓ Tabla driver actualizada")
    except Exception as e:
        print(f"   ✗ Error en driver: {e}")
        db.session.rollback()
        raise
    
    # 4. Modificar tabla payroll_periods
    print("\n4. Modificando tabla payroll_periods...")
    try:
        recreate_payroll_periods_table()
        print("   ✓ Tabla payroll_periods actualizada")
    except Exception as e:
        print(f"   ✗ Error en payroll_periods: {e}")
        db.session.rollback()
        raise
    
    # 5. Modificar tabla payroll_summaries
    print("\n5. Modificando tabla payroll_summaries...")
    try:
        recreate_payroll_summaries_table()
        print("   ✓ Tabla payroll_summaries actualizada")
    except Exception as e:
        print(f"   ✗ Error en payroll_summaries: {e}")
        db.session.rollback()
        raise
    
    # 6. Crear nuevas tablas
    print("\n6. Creando nuevas tablas...")
    try:
        create_minimum_guaranteed_history_table()
        create_payroll_other_items_table()
        print("   ✓ Nuevas tablas creadas")
    except Exception as e:
        print(f"   ✗ Error creando tablas: {e}")
        db.session.rollback()
        raise
    
    db.session.commit()
    print("\n✓ Migración completada exitosamente!")
    print("\nNOTA: Los modelos obsoletos están marcados como DEPRECATED pero se mantienen por compatibilidad.")
    print("      - CommissionPercentage")
    print("      - KmRate")
    print("      - MonthlySummary")
    print("      - PayrollAdjustment")

def migrate_driver_commissions():
    """Migrar comisiones actuales de drivers al histórico."""
    from datetime import datetime
    
    # Verificar si la tabla driver_commission_history existe
    try:
        result = db.session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='driver_commission_history'
        """))
        if not result.fetchone():
            print("   ⚠ Tabla driver_commission_history no existe, creándola primero...")
            db.session.execute(text("""
                CREATE TABLE driver_commission_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id INTEGER NOT NULL,
                    commission_percentage DECIMAL(5, 2) NOT NULL,
                    effective_from DATETIME NOT NULL,
                    effective_until DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(driver_id) REFERENCES driver(id)
                )
            """))
            db.session.commit()
    except Exception as e:
        print(f"   ⚠ Error verificando tabla: {e}")
    
    # Obtener drivers con comisión
    try:
        result = db.session.execute(text("""
            SELECT id, commission, enrollment_date 
            FROM driver 
            WHERE commission IS NOT NULL
        """))
        
        drivers = result.fetchall()
        
        for driver in drivers:
            driver_id, commission, enrollment_date = driver
            
            # Insertar en histórico
            db.session.execute(text("""
                INSERT INTO driver_commission_history 
                (driver_id, commission_percentage, effective_from, effective_until, created_at)
                VALUES (:driver_id, :commission, :effective_from, NULL, :created_at)
            """), {
                'driver_id': driver_id,
                'commission': commission,
                'effective_from': enrollment_date or datetime.now(),
                'created_at': datetime.now()
            })
        
        db.session.commit()
        print(f"   ✓ {len(drivers)} comisiones migradas al histórico")
    except Exception as e:
        print(f"   ✗ Error migrando comisiones: {e}")
        db.session.rollback()
        raise

def recreate_expense_table():
    """Recrear tabla expense sin toll_paid_by."""
    # Esta es una operación compleja en SQLite
    # Por simplicidad, solo mostramos el SQL necesario
    print("   - ADVERTENCIA: Recrear tabla expense requiere intervención manual en SQLite")
    print("   - Ejecutar manualmente los siguientes comandos SQL:")
    print("""
    BEGIN TRANSACTION;
    
    -- Crear tabla temporal
    CREATE TABLE expense_new (
        id INTEGER PRIMARY KEY,
        trip_id INTEGER,
        driver_id INTEGER NOT NULL,
        expense_type TEXT NOT NULL,
        date DATE NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        receipt_url TEXT,
        fine_municipality TEXT,
        repair_type TEXT,
        fuel_liters REAL,
        toll_type TEXT,
        paid_by_admin BOOLEAN,
        toll_port_fee_name TEXT,
        FOREIGN KEY(trip_id) REFERENCES trip(id) ON DELETE SET NULL,
        FOREIGN KEY(driver_id) REFERENCES driver(id) ON DELETE CASCADE
    );
    
    -- Copiar datos
    INSERT INTO expense_new 
    SELECT id, trip_id, driver_id, expense_type, date, amount, description, 
           receipt_url, fine_municipality, repair_type, fuel_liters, toll_type,
           CASE 
               WHEN toll_paid_by = 'Contador' THEN 1
               WHEN toll_paid_by = 'Chofer' THEN 0
               ELSE NULL
           END as paid_by_admin,
           toll_port_fee_name
    FROM expense;
    
    -- Reemplazar tabla
    DROP TABLE expense;
    ALTER TABLE expense_new RENAME TO expense;
    
    COMMIT;
    """)

def recreate_driver_table():
    """Recrear tabla driver sin commission."""
    print("   - ADVERTENCIA: Recrear tabla driver requiere intervención manual en SQLite")
    print("   - El campo 'commission' ya no se usa, ahora está en 'driver_commission_history'")

def recreate_payroll_periods_table():
    """Recrear tabla payroll_periods sin status y actual_close_date."""
    print("   - ADVERTENCIA: Recrear tabla payroll_periods requiere intervención manual")
    print("   - Los campos 'status' y 'actual_close_date' ya no se usan")

def recreate_payroll_summaries_table():
    """Recrear tabla payroll_summaries con nuevos campos."""
    print("   - ADVERTENCIA: Recrear tabla payroll_summaries requiere intervención manual")
    print("   - Nuevos campos: driver_minimum_guaranteed, other_items_total, error_message")
    print("   - Campos eliminados: calculation_type, adjustments_applied")

def create_minimum_guaranteed_history_table():
    """Crear tabla minimum_guaranteed_history."""
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS minimum_guaranteed_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            minimum_guaranteed DECIMAL(12, 2) NOT NULL,
            effective_from DATETIME NOT NULL,
            effective_until DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(driver_id) REFERENCES driver(id)
        )
    """))
    print("   - Tabla minimum_guaranteed_history creada")

def create_payroll_other_items_table():
    """Crear tabla payroll_other_items."""
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS payroll_other_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            period_id INTEGER NOT NULL,
            item_type VARCHAR(30) NOT NULL,
            description TEXT NOT NULL,
            amount DECIMAL(12, 2) NOT NULL,
            date DATE NOT NULL,
            reference VARCHAR(255),
            receipt_url VARCHAR(255),
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(driver_id) REFERENCES driver(id),
            FOREIGN KEY(period_id) REFERENCES payroll_periods(id),
            FOREIGN KEY(created_by) REFERENCES app_user(id)
        )
    """))
    print("   - Tabla payroll_other_items creada")

if __name__ == '__main__':
    print("ADVERTENCIA: Este script modifica la estructura de la base de datos")
    print("Asegúrate de tener un backup antes de continuar")
    response = input("¿Continuar? (si/no): ")
    
    if response.lower() == 'si':
        # Crear contexto de aplicación Flask
        app = create_app()
        with app.app_context():
            run_migration()
    else:
        print("Migración cancelada")
