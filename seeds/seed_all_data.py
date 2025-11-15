"""
Script para agregar datos de prueba completos a todas las entidades
"""
from datetime import date, timedelta
from app import create_app
from app.db import db
from app.models.app_user import AppUser
from app.models.driver import Driver
from app.models.truck import Truck
from app.models.client import Client
from app.models.load_owner import LoadOwner
from app.models.km_rate import KmRate
from app.models.commission_percentage import CommissionPercentage

def seed_all_data():
    """Agrega datos de prueba a todas las entidades"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Agregando datos de prueba a la base de datos...\n")
        
        # Verificar si ya hay datos
        existing_count = Truck.query.count() + Client.query.count() + LoadOwner.query.count()
        if existing_count > 0:
            print(f"⚠️  Ya existen {existing_count} registros en la base de datos")
            respuesta = input("¿Deseas agregar más datos de prueba? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return
        
        created_counts = {
            'users': 0,
            'drivers': 0,
            'trucks': 0,
            'clients': 0,
            'load_owners': 0,
            'km_rates': 0,
            'commission_percentages': 0
        }
        
        # 1. Crear Usuarios y Conductores
        print("👤 Creando usuarios y conductores...")
        drivers_data = [
            {
                'user': {'name': 'Juan', 'surname': 'Pérez', 'is_admin': False},
                'driver': {
                    'dni': 12345678, 'cuil': '20123456789',
                    'phone_number': '+54 9 11 1234-5678',
                    'cbu': '0170001234567890123456',
                    'active': True, 'commission': 15.5,
                    'enrollment_date': date(2023, 1, 15),
                    'termination_date': None,
                    'driver_license_due_date': date.today() + timedelta(days=365),
                    'medical_exam_due_date': date.today() + timedelta(days=180)
                }
            },
            {
                'user': {'name': 'María', 'surname': 'González', 'is_admin': False},
                'driver': {
                    'dni': 23456789, 'cuil': '27234567890',
                    'phone_number': '+54 9 11 2345-6789',
                    'cbu': '0110002345678901234567',
                    'active': True, 'commission': 18.0,
                    'enrollment_date': date(2023, 3, 10),
                    'termination_date': None,
                    'driver_license_due_date': date.today() + timedelta(days=400),
                    'medical_exam_due_date': date.today() + timedelta(days=200)
                }
            },
            {
                'user': {'name': 'Carlos', 'surname': 'Rodríguez', 'is_admin': False},
                'driver': {
                    'dni': 34567890, 'cuil': '20345678901',
                    'phone_number': '+54 9 11 3456-7890',
                    'cbu': '0720003456789012345678',
                    'active': False, 'commission': 12.0,
                    'enrollment_date': date(2022, 6, 1),
                    'termination_date': date(2024, 10, 15),
                    'driver_license_due_date': date.today() + timedelta(days=100),
                    'medical_exam_due_date': date.today() + timedelta(days=50)
                }
            }
        ]
        
        for data in drivers_data:
            user = AppUser(**data['user'])
            db.session.add(user)
            db.session.flush()
            driver = Driver(id=user.id, **data['driver'])
            db.session.add(driver)
            created_counts['users'] += 1
            created_counts['drivers'] += 1
        
        # Agregar un admin
        admin = AppUser(name='Admin', surname='Sistema', is_admin=True)
        db.session.add(admin)
        created_counts['users'] += 1
        
        print(f"  ✅ {created_counts['users']} usuarios creados")
        print(f"  ✅ {created_counts['drivers']} conductores creados")
        
        # 2. Crear Camiones
        print("\n🚛 Creando camiones...")
        trucks_data = [
            {
                'plate': 'AA123BC',
                'operational': True,
                'brand': 'Mercedes-Benz',
                'model_name': 'Actros 2046',
                'fabrication_year': 2020,
                'service_due_date': date.today() + timedelta(days=90),
                'vtv_due_date': date.today() + timedelta(days=180),
                'plate_due_date': date.today() + timedelta(days=270)
            },
            {
                'plate': 'AB456CD',
                'operational': True,
                'brand': 'Scania',
                'model_name': 'R 450',
                'fabrication_year': 2021,
                'service_due_date': date.today() + timedelta(days=120),
                'vtv_due_date': date.today() + timedelta(days=200),
                'plate_due_date': date.today() + timedelta(days=300)
            },
            {
                'plate': 'AC789DE',
                'operational': True,
                'brand': 'Volvo',
                'model_name': 'FH 540',
                'fabrication_year': 2019,
                'service_due_date': date.today() + timedelta(days=60),
                'vtv_due_date': date.today() + timedelta(days=150),
                'plate_due_date': date.today() + timedelta(days=240)
            },
            {
                'plate': 'AD012EF',
                'operational': False,
                'brand': 'Iveco',
                'model_name': 'Stralis 460',
                'fabrication_year': 2018,
                'service_due_date': date.today() + timedelta(days=30),
                'vtv_due_date': date.today() + timedelta(days=120),
                'plate_due_date': date.today() + timedelta(days=210)
            },
            {
                'plate': 'AE345FG',
                'operational': True,
                'brand': 'Ford',
                'model_name': 'Cargo 1723',
                'fabrication_year': 2022,
                'service_due_date': date.today() + timedelta(days=150),
                'vtv_due_date': date.today() + timedelta(days=250),
                'plate_due_date': date.today() + timedelta(days=330)
            }
        ]
        
        for truck_data in trucks_data:
            truck = Truck(**truck_data)
            db.session.add(truck)
            created_counts['trucks'] += 1
        
        print(f"  ✅ {created_counts['trucks']} camiones creados")
        
        # 3. Crear Clientes
        print("\n🏢 Creando clientes...")
        clients_data = [
            {'name': 'Distribuidora del Norte SA'},
            {'name': 'Logística Central'},
            {'name': 'Transportes del Sur'},
            {'name': 'Comercial Buenos Aires'},
            {'name': 'Industrias Argentinas'}
        ]
        
        for client_data in clients_data:
            client = Client(**client_data)
            db.session.add(client)
            created_counts['clients'] += 1
        
        print(f"  ✅ {created_counts['clients']} clientes creados")
        
        # 4. Crear Dueños de Carga
        print("\n📦 Creando dueños de carga...")
        load_owners_data = [
            {'name': 'Cerealera del Plata'},
            {'name': 'Acopio San Martín'},
            {'name': 'Granos del Litoral'},
            {'name': 'Agroindustria Argentina'},
            {'name': 'Cooperativa Agrícola'}
        ]
        
        for lo_data in load_owners_data:
            load_owner = LoadOwner(**lo_data)
            db.session.add(load_owner)
            created_counts['load_owners'] += 1
        
        print(f"  ✅ {created_counts['load_owners']} dueños de carga creados")
        
        # 5. Crear Tarifas por Kilómetro
        print("\n📏 Creando tarifas por kilómetro...")
        km_rates_data = [
            {'date': date(2024, 1, 1), 'rate': 150.0},
            {'date': date(2024, 4, 1), 'rate': 165.0},
            {'date': date(2024, 7, 1), 'rate': 180.0},
            {'date': date(2024, 10, 1), 'rate': 195.0},
            {'date': date(2025, 1, 1), 'rate': 210.0}
        ]
        
        for rate_data in km_rates_data:
            km_rate = KmRate(**rate_data)
            db.session.add(km_rate)
            created_counts['km_rates'] += 1
        
        print(f"  ✅ {created_counts['km_rates']} tarifas por km creadas")
        
        # 6. Crear Porcentajes de Comisión
        print("\n💰 Creando porcentajes de comisión...")
        commission_data = [
            {'date': date(2024, 1, 1), 'percentage': 15.0},
            {'date': date(2024, 4, 1), 'percentage': 16.0},
            {'date': date(2024, 7, 1), 'percentage': 17.0},
            {'date': date(2024, 10, 1), 'percentage': 18.0},
            {'date': date(2025, 1, 1), 'percentage': 19.0}
        ]
        
        for comm_data in commission_data:
            commission = CommissionPercentage(**comm_data)
            db.session.add(commission)
            created_counts['commission_percentages'] += 1
        
        print(f"  ✅ {created_counts['commission_percentages']} porcentajes de comisión creados")
        
        # Commit todo
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("="*60)
        print(f"📊 Resumen:")
        print(f"  - {created_counts['users']} usuarios")
        print(f"  - {created_counts['drivers']} conductores")
        print(f"  - {created_counts['trucks']} camiones")
        print(f"  - {created_counts['clients']} clientes")
        print(f"  - {created_counts['load_owners']} dueños de carga")
        print(f"  - {created_counts['km_rates']} tarifas por km")
        print(f"  - {created_counts['commission_percentages']} porcentajes de comisión")
        print("\n🌐 Inicia el servidor y prueba los endpoints:")
        print("  - http://localhost:5000/trucks/")
        print("  - http://localhost:5000/clients/")
        print("  - http://localhost:5000/drivers/")
        print("  - http://localhost:5000/load-owners/")
        print("  - http://localhost:5000/km-rates/")
        print("  - http://localhost:5000/commission-percentages/")

if __name__ == "__main__":
    seed_all_data()
