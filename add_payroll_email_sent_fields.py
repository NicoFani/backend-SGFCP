#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agrega campos para marcar envío de resúmenes por período.
Uso: python add_payroll_email_sent_fields.py
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app import create_app
from app.db import db


def column_exists(table_name: str, column_name: str) -> bool:
    result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
    return any(row[1] == column_name for row in result.fetchall())


def add_column_if_missing(table: str, column_sql: str, column_name: str):
    if column_exists(table, column_name):
        print(f"✅ Columna {column_name} ya existe en {table}")
        return
    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_sql}"))
    print(f"✅ Columna {column_name} agregada a {table}")


def main():
    app = create_app()
    with app.app_context():
        print("🔄 Agregando columnas de envío en payroll_periods...")
        add_column_if_missing("payroll_periods", "email_sent BOOLEAN DEFAULT 0", "email_sent")
        add_column_if_missing("payroll_periods", "email_sent_at DATETIME NULL", "email_sent_at")
        db.session.commit()
        print("✅ Migración completada")


if __name__ == '__main__':
    main()
