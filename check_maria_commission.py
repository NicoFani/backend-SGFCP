from app import create_app
from app.models.base import db
from app.models.trip import Trip
from app.models.driver import Driver
from app.models.payroll import PayrollSummary, PayrollDetail
from decimal import Decimal

app = create_app()

with app.app_context():
    driver = Driver.query.filter_by(full_name='María González').first()
    
    if not driver:
        print("Driver no encontrado")
        exit()
    
    print(f"Driver: {driver.full_name} (ID: {driver.id})")
    print(f"Comisión actual: {driver.current_commission_percentage}")
    
    # Buscar el resumen más reciente
    summary = PayrollSummary.query.filter_by(driver_id=driver.id).order_by(PayrollSummary.id.desc()).first()
    
    if summary:
        print(f"\n=== Resumen #{summary.id} - Período: {summary.period.name} ===")
        print(f"Total comisiones en resumen: ${summary.commission_from_trips}")
        
        # Obtener detalles de comisiones
        details = PayrollDetail.query.filter_by(
            summary_id=summary.id,
            detail_type='trip_commission'
        ).all()
        
        print(f"\n=== Detalles de comisiones ({len(details)} viajes) ===")
        total_from_details = Decimal('0.00')
        for detail in details:
            print(f"  - {detail.description}")
            print(f"    Monto comisión: ${detail.amount}")
            total_from_details += detail.amount
        
        print(f"\n=== Verificación ===")
        print(f"Suma de comisiones de detalles: ${total_from_details}")
        print(f"Campo commission_from_trips:    ${summary.commission_from_trips}")
        print(f"¿Coinciden?: {total_from_details == summary.commission_from_trips}")
    
    # Verificar viajes finalizados en febrero 2026
    print(f"\n=== Viajes finalizados en febrero 2026 ===")
    from datetime import date
    trips = Trip.query.filter(
        Trip.driver_id == driver.id,
        Trip.start_date >= date(2026, 2, 1),
        Trip.start_date <= date(2026, 2, 28),
        Trip.state_id == 'Finalizado'
    ).all()
    
    print(f"Total viajes: {len(trips)}")
    total_manual = Decimal('0.00')
    
    for trip in trips:
        if trip.calculated_per_km:
            base_amount = Decimal(str(trip.estimated_kms)) * Decimal(str(trip.rate))
            calc_type = "Por km"
            value = f"{trip.estimated_kms} km × ${trip.rate}/km"
        else:
            base_amount = Decimal(str(trip.load_weight_on_unload)) * Decimal(str(trip.rate))
            calc_type = "Por ton"
            value = f"{trip.load_weight_on_unload} t × ${trip.rate}/t"
        
        commission = base_amount * Decimal(str(driver.current_commission_percentage))
        total_manual += commission
        
        print(f"\n  Viaje {trip.id}: {trip.document_type} {trip.document_number}")
        print(f"    {calc_type}: {value} = ${base_amount}")
        print(f"    Comisión ({float(driver.current_commission_percentage)*100}%): ${commission}")
    
    print(f"\n=== Total calculado manualmente: ${total_manual} ===")
