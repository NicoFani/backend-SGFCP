#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para migrar la base de datos con los nuevos cambios:
- Agregar campos de documento (document_type, document_number)
- Agregar campos de descripción (origin_description, destination_description)
- Agregar campos de combustible (fuel_liters)
- Cambiar relación Trip-Driver de 1-a-muchos a muchos-a-muchos
"""

import os
from datetime import datetime
from app import create_app
from app.db import db

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migración de base de datos...")
        print("="*60)
        
        # Respaldar la BD antigua
        db_path = "sgfcp.db"
        if os.path.exists(db_path):
            # Generar nombre único para el backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"sgfcp.db.backup.{timestamp}"
            os.rename(db_path, backup_path)
            print(f"✅ Base de datos anterior respaldada en: {backup_path}")
        
        # Crear todas las tablas con el nuevo esquema
        print("📦 Creando tablas con el nuevo esquema...")
        db.create_all()
        
        print("\n✅ Migración completada exitosamente")
        print("="*60)
        print("\n⚠️  IMPORTANTE:")
        print("Los datos de la base de datos anterior se han perdido.")
        print("Ejecuta el siguiente comando para cargar datos de prueba:")
        print("  python seeds/seed_all_data.py && python seeds/seed_relationships.py")

if __name__ == '__main__':
    migrate_database()
