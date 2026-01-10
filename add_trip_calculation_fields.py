"""Agregar campos calculation_type y km_rate a la tabla trip."""
from app import create_app, db

app = create_app()

with app.app_context():
    # Agregar columnas a la tabla trip
    db.session.execute(db.text("""
        ALTER TABLE trip 
        ADD COLUMN calculation_type VARCHAR(20);
    """))
    
    db.session.execute(db.text("""
        ALTER TABLE trip 
        ADD COLUMN km_rate FLOAT;
    """))
    
    db.session.commit()
    print('✅ Columnas calculation_type y km_rate agregadas a la tabla trip')
