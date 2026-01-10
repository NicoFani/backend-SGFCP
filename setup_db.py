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

def run_command(cmd, description, cwd=None):
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    # Preparar el entorno con PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    # Ejecutar comando con el entorno correcto
    try:
        if cwd is None:
            cwd = os.path.dirname(os.path.abspath(__file__))
        
        result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
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
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    seeds_dir = os.path.join(base_dir, 'seeds')
    
    # 1. Migrar base de datos
    cmd1 = f'{sys.executable} migrate_db.py'
    if not run_command(cmd1, "Migrando base de datos"):
        return
    
    # 2. Cargar datos base (ejecutar desde seeds/ con PYTHONPATH al directorio raíz)
    cmd2 = f'{sys.executable} seed_all_data.py'
    if not run_command(cmd2, "Cargando datos base", cwd=seeds_dir):
        return
    
    # 3. Cargar relaciones
    cmd3 = f'{sys.executable} seed_relationships.py'
    if not run_command(cmd3, "Cargando datos de relaciones", cwd=seeds_dir):
        return
    
    print("\n" + "="*60)
    print("✅ BASE DE DATOS REINICIALIZADA EXITOSAMENTE")
    print("="*60)
    print("\n🚀 Puedes ejecutar el servidor con: python run.py")

if __name__ == '__main__':
    main()
