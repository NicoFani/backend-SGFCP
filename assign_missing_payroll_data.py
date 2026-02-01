"""Script para asignar comisiones y mínimos garantizados a choferes que no los tienen."""
from app import create_app, db
from app.controllers.driver_commission import DriverCommissionController
from app.controllers.minimum_guaranteed import MinimumGuaranteedController
from app.models.driver import Driver
from app.models.driver_commission_history import DriverCommissionHistory
from app.models.minimum_guaranteed_history import MinimumGuaranteedHistory
from datetime import datetime
from decimal import Decimal

app = create_app()

print("=" * 60)
print("ASIGNAR COMISIONES Y MÍNIMOS GARANTIZADOS")
print("=" * 60)

with app.app_context():
    # Obtener choferes activos
    drivers = Driver.query.filter_by(active=True).all()
    
    print(f"\nChoferes activos encontrados: {len(drivers)}")
    print()
    
    for driver in drivers:
        driver_name = f"{driver.user.name} {driver.user.surname}"
        print(f"Chofer ID {driver.id}: {driver_name}")
        
        # Verificar comisión
        has_commission = DriverCommissionHistory.query.filter_by(driver_id=driver.id).first()
        if not has_commission:
            print(f"  ❌ Sin comisión - Creando comisión del 15%...")
            try:
                DriverCommissionController.set_driver_commission(
                    driver_id=driver.id,
                    commission_percentage=15.0,  # 15%
                    effective_from=datetime(2026, 1, 1)
                )
                print(f"  ✅ Comisión creada: 15%")
            except Exception as e:
                print(f"  ⚠️  Error al crear comisión: {e}")
        else:
            print(f"  ✅ Ya tiene comisión")
        
        # Verificar mínimo garantizado
        has_minimum = MinimumGuaranteedHistory.query.filter_by(driver_id=driver.id).first()
        if not has_minimum:
            print(f"  ❌ Sin mínimo garantizado - Creando $150,000...")
            try:
                MinimumGuaranteedController.create(
                    driver_id=driver.id,
                    minimum_guaranteed=Decimal('150000.00'),
                    effective_from=datetime(2026, 1, 1)
                )
                print(f"  ✅ Mínimo garantizado creado: $150,000")
            except Exception as e:
                print(f"  ⚠️  Error al crear mínimo: {e}")
        else:
            print(f"  ✅ Ya tiene mínimo garantizado")
        
        print()
    
    print("=" * 60)
    print("✅ Proceso completado")
    print("=" * 60)
