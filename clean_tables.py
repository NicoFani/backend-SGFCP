"""Script para limpiar tablas específicas de la base de datos."""
from app import db, create_app
from app.models.payroll_detail import PayrollDetail
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_other_item import PayrollOtherItem
from app.models.expense import Expense
from app.models.advance_payment import AdvancePayment
from app.models.trip import Trip

app = create_app()
app.app_context().push()

print("=" * 60)
print("LIMPIEZA DE TABLAS - SGFCP")
print("=" * 60)
print("\nTablas a limpiar:")
print("  - payroll_details")
print("  - payroll_summaries")
print("  - expense")
print("  - trip")
print("  - payroll_other_items")
print("  - advance_payment")
print("\n⚠️  Esta operación eliminará TODOS los registros de estas tablas.")

confirm = input("\n¿Estás seguro? (escribe 'SI' para confirmar): ")

if confirm.strip().upper() != 'SI':
    print("\n❌ Operación cancelada\n")
    exit(0)

print('\n🧹 Iniciando limpieza de tablas...\n')

# Eliminar en orden (de hijos a padres para evitar errores de FK)
try:
    # 1. Payroll details (depende de summaries)
    count = PayrollDetail.query.delete()
    print(f'  ✓ payroll_details: {count} registros eliminados')

    # 2. Payroll summaries (depende de period, driver)
    count = PayrollSummary.query.delete()
    print(f'  ✓ payroll_summaries: {count} registros eliminados')

    # 3. Expenses (depende de trip, driver)
    count = Expense.query.delete()
    print(f'  ✓ expense: {count} registros eliminados')

    # 4. Trips
    count = Trip.query.delete()
    print(f'  ✓ trip: {count} registros eliminados')

    # 5. Payroll other items (depende de period, driver)
    count = PayrollOtherItem.query.delete()
    print(f'  ✓ payroll_other_items: {count} registros eliminados')

    # 6. Advance payments (depende de driver)
    count = AdvancePayment.query.delete()
    print(f'  ✓ advance_payment: {count} registros eliminados')

    db.session.commit()
    print('\n✅ Limpieza completada exitosamente\n')

except Exception as e:
    db.session.rollback()
    print(f'\n❌ Error durante la limpieza: {e}\n')
    raise