"""
Script para agregar datos de prueba de entidades con relaciones
Carga: driver_truck, advance_payment, trip, expense
"""
from datetime import date, timedelta
from app import create_app
from app.db import db
from app.models.driver import Driver
from app.models.truck import Truck
from app.models.driver_truck import DriverTruck
from app.models.advance_payment import AdvancePayment
from app.models.app_user import AppUser
from app.models.client import Client
from app.models.load_owner import LoadOwner
from app.models.trip import Trip
from app.models.expense import Expense

def seed_relationships():
    """Agrega datos de prueba con relaciones"""
    app = create_app()
    
    with app.app_context():
        print("🔗 Agregando datos de relaciones a la base de datos...\n")
        
        # Verificar que existen datos base
        drivers_count = Driver.query.count()
        trucks_count = Truck.query.count()
        clients_count = Client.query.count()
        load_owners_count = LoadOwner.query.count()
        
        if drivers_count == 0 or trucks_count == 0:
            print("❌ Error: Necesitas ejecutar primero 'python seed_all_data.py'")
            print("   No hay conductores o camiones en la base de datos.")
            return
        
        print(f"✅ Encontrados: {drivers_count} conductores, {trucks_count} camiones")
        print(f"✅ Encontrados: {clients_count} clientes, {load_owners_count} dueños de carga\n")
        
        created_counts = {
            'driver_trucks': 0,
            'advance_payments': 0,
            'trips': 0,
            'expenses': 0
        }
        
        # Obtener IDs existentes
        drivers = Driver.query.all()
        trucks = Truck.query.filter_by(operational=True).all()
        admin = AppUser.query.filter_by(is_admin=True).first()
        clients = Client.query.all()
        load_owners = LoadOwner.query.all()
        
        if not admin:
            print("⚠️  No se encontró usuario admin, creando uno...")
            admin = AppUser(name='Admin', surname='Sistema', is_admin=True)
            db.session.add(admin)
            db.session.flush()
        
        # 1. Crear asignaciones Driver-Truck
        print("🚛 Creando asignaciones conductor-camión...")
        if len(drivers) >= 3 and len(trucks) >= 3:
            driver_truck_assignments = [
                {'driver_id': drivers[0].id, 'truck_id': trucks[0].id, 'date': date(2024, 1, 15)},
                {'driver_id': drivers[0].id, 'truck_id': trucks[1].id, 'date': date(2024, 6, 1)},
                {'driver_id': drivers[1].id, 'truck_id': trucks[2].id, 'date': date(2024, 3, 10)},
                {'driver_id': drivers[1].id, 'truck_id': trucks[0].id, 'date': date(2024, 9, 15)},
            ]
            
            for dt_data in driver_truck_assignments:
                driver_truck = DriverTruck(**dt_data)
                db.session.add(driver_truck)
                created_counts['driver_trucks'] += 1
        
        print(f"  ✅ {created_counts['driver_trucks']} asignaciones creadas")
        
        # 2. Crear Anticipos
        print("\n💵 Creando anticipos de pago...")
        if len(drivers) >= 2:
            advance_payments_data = [
                {
                    'admin_id': admin.id,
                    'driver_id': drivers[0].id,
                    'date': date(2024, 11, 1),
                    'amount': 50000.0,
                    'receipt': 'REC-2024-001.pdf'
                },
                {
                    'admin_id': admin.id,
                    'driver_id': drivers[0].id,
                    'date': date(2024, 11, 15),
                    'amount': 30000.0,
                    'receipt': 'REC-2024-002.pdf'
                },
                {
                    'admin_id': admin.id,
                    'driver_id': drivers[1].id,
                    'date': date(2024, 11, 5),
                    'amount': 40000.0,
                    'receipt': 'REC-2024-003.pdf'
                },
                {
                    'admin_id': admin.id,
                    'driver_id': drivers[1].id,
                    'date': date(2024, 11, 20),
                    'amount': 25000.0,
                    'receipt': None
                }
            ]
            
            for ap_data in advance_payments_data:
                advance_payment = AdvancePayment(**ap_data)
                db.session.add(advance_payment)
                created_counts['advance_payments'] += 1
        
        print(f"  ✅ {created_counts['advance_payments']} anticipos creados")
        
        # 3. Crear Viajes
        print("\n🗺️  Creando viajes...")
        if len(drivers) >= 2 and len(clients) >= 2 and len(load_owners) >= 2:
            trips_data = [
                {
                    'document_number': 1001,
                    'origin': 'Buenos Aires',
                    'destination': 'Rosario',
                    'estimated_kms': 300.0,
                    'start_date': date(2024, 11, 1),
                    'end_date': date(2024, 11, 2),
                    'load_weight_on_load': 25000.0,
                    'load_weight_on_unload': 24800.0,
                    'rate_per_ton': 1500.0,
                    'fuel_on_client': False,
                    'client_advance_payment': 10000.0,
                    'state_id': 'Finalizado',
                    'driver_id': drivers[0].id,
                    'client_id': clients[0].id,
                    'load_owner_id': load_owners[0].id
                },
                {
                    'document_number': 1002,
                    'origin': 'Córdoba',
                    'destination': 'Mendoza',
                    'estimated_kms': 600.0,
                    'start_date': date(2024, 11, 5),
                    'end_date': date(2024, 11, 7),
                    'load_weight_on_load': 28000.0,
                    'load_weight_on_unload': 27900.0,
                    'rate_per_ton': 1800.0,
                    'fuel_on_client': True,
                    'client_advance_payment': 15000.0,
                    'state_id': 'Finalizado',
                    'driver_id': drivers[1].id,
                    'client_id': clients[1].id,
                    'load_owner_id': load_owners[1].id
                },
                {
                    'document_number': 1003,
                    'origin': 'Santa Fe',
                    'destination': 'Buenos Aires',
                    'estimated_kms': 470.0,
                    'start_date': date(2024, 11, 10),
                    'end_date': date(2024, 11, 11),
                    'load_weight_on_load': 22000.0,
                    'load_weight_on_unload': 21950.0,
                    'rate_per_ton': 1600.0,
                    'fuel_on_client': False,
                    'client_advance_payment': 8000.0,
                    'state_id': 'Finalizado',
                    'driver_id': drivers[0].id,
                    'client_id': clients[0].id,
                    'load_owner_id': load_owners[0].id
                },
                {
                    'document_number': 1004,
                    'origin': 'Buenos Aires',
                    'destination': 'Tucumán',
                    'estimated_kms': 1200.0,
                    'start_date': date(2024, 11, 15),
                    'end_date': None,
                    'load_weight_on_load': 30000.0,
                    'load_weight_on_unload': None,
                    'rate_per_ton': 2000.0,
                    'fuel_on_client': False,
                    'client_advance_payment': 20000.0,
                    'state_id': 'En curso',
                    'driver_id': drivers[1].id,
                    'client_id': clients[1].id,
                    'load_owner_id': load_owners[1].id
                },
                {
                    'document_number': None,
                    'origin': 'Rosario',
                    'destination': 'Córdoba',
                    'estimated_kms': 400.0,
                    'start_date': date(2024, 11, 20),
                    'end_date': None,
                    'load_weight_on_load': None,
                    'load_weight_on_unload': None,
                    'rate_per_ton': 1700.0,
                    'fuel_on_client': False,
                    'client_advance_payment': None,
                    'state_id': 'Pendiente',
                    'driver_id': drivers[0].id,
                    'client_id': clients[0].id,
                    'load_owner_id': load_owners[0].id
                }
            ]
            
            for trip_data in trips_data:
                trip = Trip(**trip_data)
                db.session.add(trip)
                db.session.flush()  # Obtener ID del viaje
                created_counts['trips'] += 1
                
                # 4. Crear Gastos solo para viajes finalizados
                if trip_data['state_id'] == 'Finalizado':
                    expenses_for_trip = []
                    
                    # Combustible
                    expenses_for_trip.append({
                        'trip_id': trip.id,
                        'expense_type': 'Combustible',
                        'date': trip.start_date,
                        'amount': 35000.0,
                        'description': 'Carga de combustible',
                        'receipt_url': f'fuel-{trip.id}.pdf',
                        'fuel_liters': 250.0,
                        'fine_municipality': None,
                        'repair_type': None,
                        'toll_type': None,
                        'toll_paid_by': None
                    })
                    
                    # Peaje
                    expenses_for_trip.append({
                        'trip_id': trip.id,
                        'expense_type': 'Peaje',
                        'date': trip.start_date,
                        'amount': 4500.0,
                        'description': 'Peaje ruta nacional',
                        'receipt_url': f'toll-{trip.id}.pdf',
                        'fuel_liters': None,
                        'fine_municipality': None,
                        'repair_type': None,
                        'toll_type': 'Peaje de ruta',
                        'toll_paid_by': 'Chofer'
                    })
                    
                    # Viáticos
                    expenses_for_trip.append({
                        'trip_id': trip.id,
                        'expense_type': 'Viáticos',
                        'date': trip.start_date,
                        'amount': 8000.0,
                        'description': 'Viáticos del conductor',
                        'receipt_url': None,
                        'fuel_liters': None,
                        'fine_municipality': None,
                        'repair_type': None,
                        'toll_type': None,
                        'toll_paid_by': None
                    })
                    
                    for expense_data in expenses_for_trip:
                        expense = Expense(**expense_data)
                        db.session.add(expense)
                        created_counts['expenses'] += 1
        
        print(f"  ✅ {created_counts['trips']} viajes creados")
        print(f"  ✅ {created_counts['expenses']} gastos creados")
        
        # Commit todo
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 DATOS DE RELACIONES CREADOS EXITOSAMENTE")
        print("="*60)
        print(f"📊 Resumen:")
        print(f"  - {created_counts['driver_trucks']} asignaciones conductor-camión")
        print(f"  - {created_counts['advance_payments']} anticipos de pago")
        print(f"  - {created_counts['trips']} viajes")
        print(f"  - {created_counts['expenses']} gastos")
        print("\n🌐 Prueba los endpoints:")
        print("  - http://localhost:5000/driver-trucks/")
        print("  - http://localhost:5000/advance-payments/")
        print("  - http://localhost:5000/trips/")
        print("  - http://localhost:5000/expenses/")
        print("\n💡 Tip: Usa el archivo sgfcp.db con SQLite Viewer para ver las relaciones")

if __name__ == "__main__":
    seed_relationships()
