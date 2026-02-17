"""
Script para cargar valores por defecto de comisión y mínimo garantizado para choferes.
Crea registros en driver_commission_history y minimum_guaranteed_history.
"""
from datetime import datetime
from app import create_app
from app.models.base import db
from app.models.driver import Driver
from app.models.driver_commission_history import DriverCommissionHistory
from app.models.minimum_guaranteed_history import MinimumGuaranteedHistory

def load_driver_defaults():
    """Carga valores por defecto para todos los choferes."""
    app = create_app()
    
    with app.app_context():
        try:
            print("Iniciando carga de valores por defecto para choferes...\n")
            
            # Valores por defecto según el sistema
            DEFAULT_COMMISSION = 0.18  # 18% como decimal
            DEFAULT_MINIMUM_GUARANTEED = 1000000.00  # $1.000.000
            
            # Obtener todos los choferes activos
            drivers = Driver.query.all()
            
            if not drivers:
                print("⚠️  No se encontraron choferes en la base de datos.")
                return
            
            print(f"Se encontraron {len(drivers)} chofer(es)")
            print(f"\nValores por defecto a cargar:")
            print(f"  • Comisión: {DEFAULT_COMMISSION * 100}%")
            print(f"  • Mínimo garantizado: ${DEFAULT_MINIMUM_GUARANTEED:,.2f}")
            print()
            
            drivers_processed = 0
            drivers_skipped = 0
            
            for driver in drivers:
                driver_name = f"{driver.user.name} {driver.user.surname}" if driver.user else f"Driver ID {driver.id}"
                print(f"Procesando: {driver_name} (ID: {driver.id})")
                
                # Verificar si ya existe un registro de comisión vigente
                existing_commission = DriverCommissionHistory.query.filter_by(
                    driver_id=driver.id,
                    effective_until=None
                ).first()
                
                if existing_commission:
                    print(f"  ⚠️  Ya existe un registro de comisión vigente ({existing_commission.commission_percentage * 100}%)")
                else:
                    # Crear registro de comisión
                    commission_record = DriverCommissionHistory(
                        driver_id=driver.id,
                        commission_percentage=DEFAULT_COMMISSION,
                        effective_from=datetime.now(),
                        effective_until=None  # NULL = vigente actualmente
                    )
                    db.session.add(commission_record)
                    print(f"  ✓ Registro de comisión creado: {DEFAULT_COMMISSION * 100}%")
                
                # Verificar si ya existe un registro de mínimo garantizado vigente
                existing_minimum = MinimumGuaranteedHistory.query.filter_by(
                    driver_id=driver.id,
                    effective_until=None
                ).first()
                
                if existing_minimum:
                    print(f"  ⚠️  Ya existe un registro de mínimo garantizado vigente (${existing_minimum.minimum_guaranteed:,.2f})")
                    drivers_skipped += 1
                else:
                    # Crear registro de mínimo garantizado
                    minimum_record = MinimumGuaranteedHistory(
                        driver_id=driver.id,
                        minimum_guaranteed=DEFAULT_MINIMUM_GUARANTEED,
                        effective_from=datetime.now(),
                        effective_until=None  # NULL = vigente actualmente
                    )
                    db.session.add(minimum_record)
                    print(f"  ✓ Registro de mínimo garantizado creado: ${DEFAULT_MINIMUM_GUARANTEED:,.2f}")
                
                if not existing_commission or not existing_minimum:
                    drivers_processed += 1
                
                print()
            
            # Commit de todas las operaciones
            db.session.commit()
            
            print("=" * 60)
            print(f"✅ Carga completada exitosamente!")
            print(f"   • Choferes procesados: {drivers_processed}")
            if drivers_skipped > 0:
                print(f"   • Choferes omitidos (ya tenían registros): {drivers_skipped}")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la carga: {e}")
            raise

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE CARGA DE VALORES POR DEFECTO PARA CHOFERES")
    print("=" * 60)
    print("\nEste script creará registros en:")
    print("  • driver_commission_history (18%)")
    print("  • minimum_guaranteed_history ($1.000.000)")
    print("\nPara todos los choferes que no tengan registros vigentes.\n")
    
    respuesta = input("¿Deseas continuar? (escribí 'SI' para confirmar): ")
    
    if respuesta.strip().upper() == "SI":
        print("\nProcediendo con la carga...\n")
        load_driver_defaults()
    else:
        print("\n❌ Operación cancelada.")
