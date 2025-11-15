"""
Script para agregar datos de prueba (seed data) a la base de datos
Crea conductores de ejemplo
"""
from datetime import date, timedelta
from app import create_app
from app.db import db
from app.models.app_user import AppUser
from app.models.driver import Driver

def seed_drivers():
    """Agrega conductores de prueba a la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Agregando datos de prueba...")
        
        # Verificar si ya hay conductores
        existing_drivers = Driver.query.count()
        if existing_drivers > 0:
            print(f"⚠️  Ya existen {existing_drivers} conductor(es) en la base de datos")
            respuesta = input("¿Deseas agregar más conductores de prueba? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return
        
        # Crear usuarios base para los conductores
        drivers_data = [
            {
                'user': {
                    'name': 'Juan',
                    'surname': 'Pérez',
                    'is_admin': False
                },
                'driver': {
                    'dni': 12345678,
                    'cuil': '20123456789',
                    'phone_number': '+54 9 11 1234-5678',
                    'cbu': '0170001234567890123456',
                    'active': True,
                    'commission': 15.5,
                    'enrollment_date': date(2023, 1, 15),
                    'termination_date': None,
                    'driver_license_due_date': date.today() + timedelta(days=365),
                    'medical_exam_due_date': date.today() + timedelta(days=180)
                }
            },
            {
                'user': {
                    'name': 'María',
                    'surname': 'González',
                    'is_admin': False
                },
                'driver': {
                    'dni': 23456789,
                    'cuil': '27234567890',
                    'phone_number': '+54 9 11 2345-6789',
                    'cbu': '0110002345678901234567',
                    'active': True,
                    'commission': 18.0,
                    'enrollment_date': date(2023, 3, 10),
                    'termination_date': None,
                    'driver_license_due_date': date.today() + timedelta(days=400),
                    'medical_exam_due_date': date.today() + timedelta(days=200)
                }
            },
            {
                'user': {
                    'name': 'Carlos',
                    'surname': 'Rodríguez',
                    'is_admin': False
                },
                'driver': {
                    'dni': 34567890,
                    'cuil': '20345678901',
                    'phone_number': '+54 9 11 3456-7890',
                    'cbu': '0720003456789012345678',
                    'active': False,
                    'commission': 12.0,
                    'enrollment_date': date(2022, 6, 1),
                    'termination_date': date(2024, 10, 15),
                    'driver_license_due_date': date.today() + timedelta(days=100),
                    'medical_exam_due_date': date.today() + timedelta(days=50)
                }
            }
        ]
        
        conductores_creados = 0
        
        for data in drivers_data:
            # Crear el usuario
            user = AppUser(**data['user'])
            db.session.add(user)
            db.session.flush()  # Obtener el ID sin hacer commit
            
            # Crear el conductor vinculado al usuario
            driver = Driver(id=user.id, **data['driver'])
            db.session.add(driver)
            
            conductores_creados += 1
            print(f"✅ Conductor creado: {user.name} {user.surname} (DNI: {driver.dni})")
        
        # Guardar todos los cambios
        db.session.commit()
        
        print(f"\n🎉 Se agregaron {conductores_creados} conductor(es) de prueba")
        print("\n📊 Resumen de conductores en la base de datos:")
        
        # Mostrar todos los conductores
        all_drivers = Driver.query.join(AppUser).all()
        for driver in all_drivers:
            estado = "Activo" if driver.active else "Inactivo"
            print(f"  - ID: {driver.id} | {driver.app_user.name} {driver.app_user.surname} | DNI: {driver.dni} | Estado: {estado}")

if __name__ == "__main__":
    seed_drivers()
