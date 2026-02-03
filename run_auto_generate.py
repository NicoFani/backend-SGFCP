from app import create_app
from app.scheduler import generate_auto_payroll_summaries

app = create_app()

with app.app_context():
    print("=== Ejecutando generación automática de resúmenes de nómina ===\n")
    generate_auto_payroll_summaries()
    print("\n=== Generación completada ===")
