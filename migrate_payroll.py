"""Script para crear las tablas del módulo de liquidación de sueldos."""
import sys
from app import create_app
from app.models.base import db
from app.models.payroll_period import PayrollPeriod
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_detail import PayrollDetail
from app.models.payroll_adjustment import PayrollAdjustment
from app.models.payroll_settings import PayrollSettings
from app.models.driver_commission_history import DriverCommissionHistory


def create_payroll_tables():
    """Crear las tablas del módulo de liquidación."""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creando tablas del módulo de liquidación...")
            
            # Crear todas las tablas
            db.create_all()
            
            print("✓ Tablas creadas exitosamente:")
            print("  - payroll_periods")
            print("  - payroll_summaries")
            print("  - payroll_details")
            print("  - payroll_adjustments")
            print("  - payroll_settings")
            print("  - driver_commission_history")
            
            # Crear configuración inicial si no existe
            existing_settings = PayrollSettings.query.first()
            if not existing_settings:
                print("\nCreando configuración inicial...")
                from datetime import datetime
                settings = PayrollSettings(
                    guaranteed_minimum=0.0,
                    default_commission_percentage=18.0,
                    auto_generation_day=31,
                    effective_from=datetime.utcnow()
                )
                db.session.add(settings)
                db.session.commit()
                print("✓ Configuración inicial creada")
            else:
                print("\n✓ Configuración ya existe")
            
            print("\n¡Migración completada exitosamente!")
            return True
            
        except Exception as e:
            print(f"\n✗ Error al crear tablas: {str(e)}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = create_payroll_tables()
    sys.exit(0 if success else 1)
