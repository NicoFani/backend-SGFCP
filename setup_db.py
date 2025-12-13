#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para reinicializar la base de datos con los nuevos cambios
Uso: python setup_db.py
"""

import os
import sys
import subprocess

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    # Ejecutar comando en el mismo proceso para que vea el PYTHONPATH
    try:
        result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode != 0:
            print(f"❌ Error ejecutando: {cmd}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n🔄 REINICIALIZANDO BASE DE DATOS")
    print("="*60)
    
    # Establecer PYTHONPATH para los subprocesos
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Migrar base de datos
    cmd1 = f'{sys.executable} migrate_db.py'
    if not run_command(cmd1, "Migrando base de datos"):
        return
    
    # 2. Cargar datos base
    cmd2 = f'cd seeds && {sys.executable} seed_all_data.py'
    if not run_command(cmd2, "Cargando datos base"):
        return
    
    # 3. Cargar relaciones
    cmd3 = f'cd seeds && {sys.executable} seed_relationships.py'
    if not run_command(cmd3, "Cargando datos de relaciones"):
        return
    
    print("\n" + "="*60)
    print("✅ BASE DE DATOS REINICIALIZADA EXITOSAMENTE")
    print("="*60)
    print("\n🚀 Puedes ejecutar el servidor con: python run.py")

if __name__ == '__main__':
    main()
