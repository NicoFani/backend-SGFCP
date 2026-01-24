"""Script para ver detalles del resumen de liquidación."""
from app import create_app
from app.models.base import db
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_detail import PayrollDetail
from app.models.trip import Trip
from app.models.expense import Expense
from app.models.advance_payment import AdvancePayment
import json

app = create_app()

with app.app_context():
    summary = PayrollSummary.query.get(13)
    
    if not summary:
        print("No se encontró el resumen #13")
    else:
        print(f"=== RESUMEN #{summary.id} ===")
        print(f"Chofer: {summary.driver.user.name} {summary.driver.user.surname}")
        print(f"Periodo: {summary.period.month}/{summary.period.year}")
        print(f"Porcentaje comisión: {summary.driver_commission_percentage}%")
        print(f"Mínimo garantizado: ${summary.driver_minimum_guaranteed}")
        print()
        print(f"Comisión por viajes: ${summary.commission_from_trips}")
        print(f"Gastos a reintegrar: ${summary.expenses_to_reimburse}")
        print(f"Gastos a descontar: ${summary.expenses_to_deduct}")
        print(f"Mínimo garantizado aplicado: ${summary.guaranteed_minimum_applied}")
        print(f"Adelantos descontados: ${summary.advances_deducted}")
        print(f"Otros conceptos: ${summary.other_items_total}")
        print(f"TOTAL: ${summary.total_amount}")
        
        print(f"\n=== DETALLES DEL CÁLCULO ===\n")
        
        details = PayrollDetail.query.filter_by(summary_id=13).all()
        
        for detail in details:
            print(f"\n{detail.detail_type.upper()}: {detail.description}")
            print(f"  Monto: ${detail.amount}")
            
            if detail.calculation_data:
                calc = json.loads(detail.calculation_data)
                if detail.detail_type == 'trip_commission':
                    print(f"  Tipo de cálculo: {calc.get('calculation_type', 'N/A')}")
                    if calc.get('calculation_type') == 'per_tonnage':
                        print(f"  Toneladas: {calc.get('tonnage', 'N/A')}")
                        print(f"  Tarifa por tonelada: ${calc.get('rate_per_ton', 'N/A')}")
                        print(f"  Monto base: ${calc.get('base_amount', 'N/A')}")
                    elif calc.get('calculation_type') == 'per_km':
                        print(f"  Kilómetros: {calc.get('kilometers', 'N/A')}")
                        print(f"  Tarifa por km: ${calc.get('rate_per_km', 'N/A')}")
                        print(f"  Monto base: ${calc.get('base_amount', 'N/A')}")
                    print(f"  Porcentaje comisión: {calc.get('commission_percentage', 'N/A')}%")
                    print(f"  Comisión calculada: ${calc.get('commission_amount', 'N/A')}")
        
        # Ver viajes incluidos
        print(f"\n=== VIAJES DEL PERÍODO ===\n")
        trips = Trip.query.filter_by(driver_id=summary.driver_id).filter(
            Trip.start_date >= summary.period.start_date,
            Trip.start_date <= summary.period.end_date,
            Trip.state_id == 'Finalizado'
        ).all()
        
        for trip in trips:
            print(f"Viaje #{trip.id}: {trip.document_type} {trip.document_number}")
            print(f"  {trip.origin} → {trip.destination}")
            print(f"  Peso descarga: {trip.load_weight_on_unload} kg")
            print(f"  Tarifa: ${trip.rate}")
            print(f"  Por km: {trip.calculated_per_km}")
        
        # Ver gastos
        print(f"\n=== GASTOS DEL PERÍODO ===\n")
        expenses = Expense.query.filter_by(driver_id=summary.driver_id).filter(
            Expense.date >= summary.period.start_date,
            Expense.date <= summary.period.end_date
        ).all()
        
        for expense in expenses:
            print(f"Gasto #{expense.id}: {expense.description}")
            print(f"  Monto: ${expense.amount}")
            print(f"  Deducir de sueldo: {expense.deduct_from_salary}")
        
        # Ver adelantos
        print(f"\n=== ADELANTOS DEL PERÍODO ===\n")
        advances = AdvancePayment.query.filter_by(driver_id=summary.driver_id).filter(
            AdvancePayment.payment_date >= summary.period.start_date,
            AdvancePayment.payment_date <= summary.period.end_date
        ).all()
        
        for advance in advances:
            print(f"Adelanto #{advance.id}")
            print(f"  Monto: ${advance.amount}")
            print(f"  Fecha: {advance.payment_date}")
