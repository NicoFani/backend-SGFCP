"""
Script para limpiar datos de prueba de la base de datos.
Elimina registros de tablas específicas respetando las relaciones de claves foráneas.
"""
from app import create_app
from app.models.base import db
from sqlalchemy import text

def clean_test_data():
    """Limpia datos de prueba de varias tablas."""
    app = create_app()
    
    with app.app_context():
        try:
            print("Iniciando limpieza de datos de prueba...\n")
            
            # Orden de eliminación respetando claves foráneas
            # 1. Detalles de nómina (dependen de payroll_summaries)
            result = db.session.execute(text("DELETE FROM payroll_details"))
            print(f"✓ Eliminados {result.rowcount} registros de payroll_details")
            
            # 2. Otros items de nómina (dependen de payroll_summaries y posiblemente driver)
            result = db.session.execute(text("DELETE FROM payroll_other_items"))
            print(f"✓ Eliminados {result.rowcount} registros de payroll_other_items")
            
            # 3. Resúmenes de nómina
            result = db.session.execute(text("DELETE FROM payroll_summaries"))
            print(f"✓ Eliminados {result.rowcount} registros de payroll_summaries")
            
            # 4. Gastos (dependen de trip y driver)
            result = db.session.execute(text("DELETE FROM expense"))
            print(f"✓ Eliminados {result.rowcount} registros de expense")
            
            # 5. Viajes
            result = db.session.execute(text("DELETE FROM trip"))
            print(f"✓ Eliminados {result.rowcount} registros de trip")
            
            # 6. Adelantos (dependen de driver)
            result = db.session.execute(text("DELETE FROM advance_payment"))
            print(f"✓ Eliminados {result.rowcount} registros de advance_payment")
            
            # 7. Historial de comisiones de choferes
            result = db.session.execute(text("DELETE FROM driver_commission_history"))
            print(f"✓ Eliminados {result.rowcount} registros de driver_commission_history")
            
            # 8. Historial de mínimo garantizado
            result = db.session.execute(text("DELETE FROM minimum_guaranteed_history"))
            print(f"✓ Eliminados {result.rowcount} registros de minimum_guaranteed_history")
            
            # 9. Notificaciones
            result = db.session.execute(text("DELETE FROM notification"))
            print(f"✓ Eliminados {result.rowcount} registros de notification")
            
            # 10. Driver-Truck relationships (si existe)
            try:
                result = db.session.execute(text("DELETE FROM driver_truck WHERE driver_id IN (5, 6)"))
                print(f"✓ Eliminados {result.rowcount} registros de driver_truck para drivers 5 y 6")
            except Exception as e:
                print(f"  (driver_truck: {e})")
            
            # 11. Choferes específicos (id 5 y 6)
            result = db.session.execute(text("DELETE FROM driver WHERE id IN (5, 6)"))
            print(f"✓ Eliminados {result.rowcount} registros de driver (ids 5 y 6)")
            
            # 12. Usuarios específicos (id 5 y 6)
            result = db.session.execute(text("DELETE FROM app_user WHERE id IN (5, 6)"))
            print(f"✓ Eliminados {result.rowcount} registros de app_user (ids 5 y 6)")
            
            # Commit de todas las operaciones
            db.session.commit()
            print("\n✅ Limpieza completada exitosamente!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la limpieza: {e}")
            raise

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE LIMPIEZA DE DATOS DE PRUEBA")
    print("=" * 60)
    print("\nEste script eliminará PERMANENTEMENTE los siguientes datos:")
    print("  • Todos los viajes")
    print("  • Todos los resúmenes de nómina y sus detalles")
    print("  • Todos los otros conceptos de nómina")
    print("  • Todos los gastos")
    print("  • Todos los adelantos")
    print("  • Todo el historial de comisiones")
    print("  • Todo el historial de mínimo garantizado")
    print("  • Todas las notificaciones")
    print("  • Choferes y usuarios con id 5 y 6")
    print("\n⚠️  Esta acción NO SE PUEDE DESHACER ⚠️\n")
    
    respuesta = input("¿Estás seguro de que querés continuar? (escribí 'SI' para confirmar): ")
    
    if respuesta.strip().upper() == "SI":
        print("\nProcediendo con la limpieza...\n")
        clean_test_data()
    else:
        print("\n❌ Operación cancelada. No se eliminó ningún dato.")
