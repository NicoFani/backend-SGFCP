"""
Seed data para la tabla LoadType
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.db import db
from app.models.load_type import LoadType

def seed_load_types():
    app = create_app()
    
    with app.app_context():
        print("\n=== SEEDING LOAD TYPES ===\n")
        
        # Tipos de carga por tonelada (default_calculated_per_km = False)
        tonnage_types = [
            'Girasol',
            'Maíz',
            'Soja',
            'Trigo',
            'Cebada',
            'Pellets',
            'Sorgo',
            'Espiga'
        ]
        
        # Tipos de carga por km (default_calculated_per_km = True)
        km_types = [
            'Bolsones para reparto',
            'Semillas'
        ]
        
        # Agregar tipos por tonelada
        print("Agregando tipos de carga por TONELADA:")
        for name in tonnage_types:
            existing = LoadType.query.filter_by(name=name).first()
            if not existing:
                load_type = LoadType(name=name, default_calculated_per_km=False)
                db.session.add(load_type)
                print(f"  ✓ {name}")
            else:
                print(f"  - {name} (ya existe)")
        
        # Agregar tipos por km
        print("\nAgregando tipos de carga por KM:")
        for name in km_types:
            existing = LoadType.query.filter_by(name=name).first()
            if not existing:
                load_type = LoadType(name=name, default_calculated_per_km=True)
                db.session.add(load_type)
                print(f"  ✓ {name}")
            else:
                print(f"  - {name} (ya existe)")
        
        db.session.commit()
        
        # Mostrar resumen
        total = LoadType.query.count()
        print(f"\n=== SEED COMPLETADO: {total} tipos de carga en total ===\n")

if __name__ == '__main__':
    seed_load_types()
