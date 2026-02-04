#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crea la tabla de notificaciones si no existe.
Uso: python add_notification_table.py
"""

import os
import sys

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.db import db


def main():
    app = create_app()
    with app.app_context():
        print("🔄 Creando tabla notification si no existe...")
        db.create_all()
        print("✅ Tabla notification creada/verificada")


if __name__ == '__main__':
    main()
