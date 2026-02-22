"""
Migración: Agregar campos balance_in_favor y balance_against a payroll_summaries.

Este script agrega dos nuevos campos a la tabla payroll_summaries:
- balance_in_favor: suma de todas las ganancias (conceptos positivos)
- balance_against: suma de todas las deducciones (conceptos negativos, guardado como valor positivo)

Ejecutar este script una vez antes de usar la nueva funcionalidad.
"""

import os
import sys
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from app.models.base import db
from app.models.payroll_summary import PayrollSummary
from sqlalchemy import text

def add_balance_columns():
    """Agregar las columnas balance_in_favor y balance_against."""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('payroll_summaries')]
            
            if 'balance_in_favor' in columns and 'balance_against' in columns:
                print("✓ Las columnas ya existen, no es necesario migrar.")
                return
            
            print("Agregando columnas balance_in_favor y balance_against...")
            
            # Agregar las columnas
            if 'balance_in_favor' not in columns:
                db.session.execute(text(
                    'ALTER TABLE payroll_summaries ADD COLUMN balance_in_favor NUMERIC(12, 2) DEFAULT 0.0'
                ))
                print("✓ Columna balance_in_favor agregada")
            
            if 'balance_against' not in columns:
                db.session.execute(text(
                    'ALTER TABLE payroll_summaries ADD COLUMN balance_against NUMERIC(12, 2) DEFAULT 0.0'
                ))
                print("✓ Columna balance_against agregada")
            
            db.session.commit()
            
            # Actualizar valores existentes
            print("\nActualizando valores existentes...")
            summaries = PayrollSummary.query.all()
            
            for summary in summaries:
                # Calcular saldo a favor (suma de ganancias)
                balance_in_favor = (
                    summary.commission_from_trips +
                    summary.expenses_to_reimburse +
                    summary.guaranteed_minimum_applied +
                    (summary.other_items_total if summary.other_items_total > 0 else Decimal('0.00'))
                )
                
                # Calcular saldo en contra (suma de deducciones, como valor positivo)
                balance_against = (
                    summary.expenses_to_deduct +
                    summary.advances_deducted +
                    (abs(summary.other_items_total) if summary.other_items_total < 0 else Decimal('0.00'))
                )
                
                # Actualizar los campos
                summary.balance_in_favor = balance_in_favor
                summary.balance_against = balance_against
            
            db.session.commit()
            print(f"✓ Actualizados {len(summaries)} resúmenes existentes")
            print("\n¡Migración completada exitosamente!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    add_balance_columns()
