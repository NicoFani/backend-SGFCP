"""
Script para agregar resúmenes mensuales de prueba
Genera monthly_summary basado en los viajes existentes
"""
from datetime import datetime, date
from app import create_app
from app.db import db
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.expense import Expense
from app.models.advance_payment import AdvancePayment
from app.models.monthly_summary import MonthlySummary

def seed_monthly_summaries():
    """Agrega resúmenes mensuales de prueba"""
    app = create_app()
    
    with app.app_context():
        print("📊 Generando resúmenes mensuales...\n")
        
        # Verificar que existen viajes
        trips_count = Trip.query.count()
        if trips_count == 0:
            print("❌ Error: No hay viajes en la base de datos")
            print("   Ejecuta primero: python seed_relationships.py")
            return
        
        print(f"✅ Encontrados {trips_count} viajes\n")
        
        # Obtener conductores activos
        drivers = Driver.query.filter_by(active=True).all()
        
        if len(drivers) == 0:
            print("❌ Error: No hay conductores activos")
            return
        
        created_count = 0
        
        # Crear resúmenes mensuales para cada conductor activo
        for driver in drivers:
            # Obtener viajes finalizados del conductor en noviembre 2024
            trips = Trip.query.filter_by(
                driver_id=driver.id,
                state_id='Finalizado'
            ).filter(
                Trip.start_date >= date(2024, 11, 1),
                Trip.start_date < date(2024, 12, 1)
            ).all()
            
            if len(trips) == 0:
                print(f"⚠️  Sin viajes finalizados para conductor ID {driver.id} en nov/2024")
                continue
            
            # Calcular totales
            total_tons = sum(trip.load_weight_on_unload or 0 for trip in trips)
            total_billed = sum((trip.load_weight_on_unload or 0) * (trip.rate_per_ton or 0) for trip in trips)
            total_kms = sum(trip.estimated_kms or 0 for trip in trips)
            
            # Calcular gastos
            trip_ids = [trip.id for trip in trips]
            expenses = Expense.query.filter(Expense.trip_id.in_(trip_ids)).all()
            total_expenses = sum(expense.amount for expense in expenses)
            
            # Calcular anticipos del mes
            advance_payments = AdvancePayment.query.filter_by(
                driver_id=driver.id
            ).filter(
                AdvancePayment.date >= date(2024, 11, 1),
                AdvancePayment.date < date(2024, 12, 1)
            ).all()
            total_advance_payments = sum(ap.amount for ap in advance_payments)
            
            # Calcular comisión (usar la comisión del conductor)
            total_commission = total_billed * (driver.commission / 100)
            
            # Calcular liquidación final
            final_settlement = total_commission - total_expenses - total_advance_payments
            
            # Crear resumen mensual
            summary_data = {
                'driver_id': driver.id,
                'month': 11,
                'year': 2024,
                'generated_at': datetime.now(),
                'calculation_method': 'Porcentaje',  # Usar enum en español
                'trips_counter': len(trips),
                'trips_count': len(trips),
                'km_traveled': total_kms,
                'total_tons': total_tons,
                'total_billed': total_billed,
                'total_commission': total_commission,
                'total_expenses': total_expenses,
                'total_advance_payments': total_advance_payments,
                'final_settlement': final_settlement,
                'pdf_url': f'summary-{driver.id}-2024-11.pdf'
            }
            
            summary = MonthlySummary(**summary_data)
            db.session.add(summary)
            created_count += 1
            
            print(f"✅ Resumen creado para conductor {driver.id}:")
            print(f"   - Viajes: {len(trips)}")
            print(f"   - Total facturado: ${total_billed:,.2f}")
            print(f"   - Comisión ({driver.commission}%): ${total_commission:,.2f}")
            print(f"   - Gastos: ${total_expenses:,.2f}")
            print(f"   - Anticipos: ${total_advance_payments:,.2f}")
            print(f"   - Liquidación final: ${final_settlement:,.2f}\n")
        
        # Commit
        db.session.commit()
        
        print("="*60)
        print(f"🎉 {created_count} RESUMEN(ES) MENSUAL(ES) CREADO(S)")
        print("="*60)
        print("\n🌐 Prueba el endpoint:")
        print("  - http://localhost:5000/monthly-summaries/")
        print("\n💡 Tip: Estos resúmenes se basan en los viajes de noviembre 2024")

if __name__ == "__main__":
    seed_monthly_summaries()
