from app import db, create_app
from app.models import (Trip, Expense, AdvancePayment, PayrollSummary, 
                         PayrollDetail, PayrollSettings, PayrollAdjustment, PayrollPeriod)

app = create_app()
app.app_context().push()

# Eliminar en orden (de hijos a padres)
print('Eliminando registros...')

# 1. Payroll details (depende de summaries)
count = PayrollDetail.query.delete()
print(f'✓ PayrollDetail: {count} registros')

# 2. Payroll summaries (depende de period, driver)
count = PayrollSummary.query.delete()
print(f'✓ PayrollSummary: {count} registros')

# 3. Payroll adjustments
count = PayrollAdjustment.query.delete()
print(f'✓ PayrollAdjustment: {count} registros')

# 4. Expenses (depende de trip, driver)
count = Expense.query.delete()
print(f'✓ Expense: {count} registros')

# 5. Advance payments (depende de driver)
count = AdvancePayment.query.delete()
print(f'✓ AdvancePayment: {count} registros')

# 6. Trip-drivers (tabla intermedia many-to-many)
result = db.session.execute(db.text('DELETE FROM trip_drivers'))
print(f'✓ trip_drivers: {result.rowcount} registros')

# 7. Trips
count = Trip.query.delete()
print(f'✓ Trip: {count} registros')

# 8. Payroll settings
count = PayrollSettings.query.delete()
print(f'✓ PayrollSettings: {count} registros')

# 9. Payroll periods
count = PayrollPeriod.query.delete()
print(f'✓ PayrollPeriod: {count} registros')

db.session.commit()
print('\n✅ Todas las tablas limpiadas correctamente')
