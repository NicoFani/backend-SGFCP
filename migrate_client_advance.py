"""Migración para agregar campo client_advance_payment a la tabla trip."""
from app import create_app
from app.models.base import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Ejecutar SQL para agregar la columna
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE trip ADD COLUMN client_advance_payment FLOAT DEFAULT 0.0'))
            conn.commit()
        print("✓ Columna client_advance_payment agregada exitosamente a la tabla trip")
    except Exception as e:
        if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
            print("✓ La columna client_advance_payment ya existe en la tabla trip")
        else:
            print(f"Error al agregar columna: {e}")
            raise
