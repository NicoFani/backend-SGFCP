"""Script para cargar períodos de liquidación 2026 y mínimos garantizados."""
from datetime import date
from decimal import Decimal
from app import create_app
from app.models.base import db
from app.models.payroll_period import PayrollPeriod
from app.models.minimum_guaranteed_history import MinimumGuaranteedHistory
from app.models.driver import Driver

app = create_app()

def seed_payroll_periods_2026():
    """Crear períodos mensuales para todo el año 2026."""
    with app.app_context():
        # Definir los días de cada mes en 2026
        months = [
            (1, 31),   # Enero
            (2, 28),   # Febrero (2026 no es bisiesto)
            (3, 31),   # Marzo
            (4, 30),   # Abril
            (5, 31),   # Mayo
            (6, 30),   # Junio
            (7, 31),   # Julio
            (8, 31),   # Agosto
            (9, 30),   # Septiembre
            (10, 31),  # Octubre
            (11, 30),  # Noviembre
            (12, 31),  # Diciembre
        ]
        
        created_count = 0
        
        for month, last_day in months:
            # Verificar si ya existe el período
            existing = PayrollPeriod.query.filter_by(year=2026, month=month).first()
            
            if existing:
                print(f"Período {month}/2026 ya existe (ID: {existing.id})")
                continue
            
            # Crear nuevo período
            period = PayrollPeriod(
                year=2026,
                month=month,
                start_date=date(2026, month, 1),
                end_date=date(2026, month, last_day)
            )
            db.session.add(period)
            created_count += 1
            print(f"✓ Creado período {month}/2026")
        
        db.session.commit()
        print(f"\nTotal períodos creados: {created_count}/12")


def seed_minimum_guaranteed():
    """Cargar mínimos garantizados actuales para cada chofer."""
    with app.app_context():
        # Obtener todos los choferes activos
        drivers = Driver.query.filter_by(active=True).all()
        
        # Mínimo garantizado por defecto: $150,000 (ajustar según necesidad)
        default_minimum = Decimal('150000.00')
        
        created_count = 0
        
        for driver in drivers:
            # Verificar si ya tiene un mínimo garantizado vigente
            existing = MinimumGuaranteedHistory.query.filter_by(
                driver_id=driver.id,
                effective_until=None  # Vigente sin fecha fin
            ).first()
            
            if existing:
                print(f"Chofer {driver.user.name} {driver.user.surname} ya tiene mínimo garantizado: ${existing.minimum_guaranteed}")
                continue
            
            # Crear registro de mínimo garantizado
            minimum = MinimumGuaranteedHistory(
                driver_id=driver.id,
                minimum_guaranteed=default_minimum,
                effective_from=date(2026, 1, 1),  # Vigente desde inicio de año
                effective_until=None  # Sin fecha fin (vigente)
            )
            db.session.add(minimum)
            created_count += 1
            print(f"✓ Creado mínimo garantizado para {driver.user.name} {driver.user.surname}: ${default_minimum}")
        
        db.session.commit()
        print(f"\nTotal mínimos garantizados creados: {created_count}/{len(drivers)}")


if __name__ == '__main__':
    print("=== Cargando períodos de liquidación 2026 ===\n")
    seed_payroll_periods_2026()
    
    print("\n=== Cargando mínimos garantizados ===\n")
    seed_minimum_guaranteed()
    
    print("\n✓ Proceso completado")
