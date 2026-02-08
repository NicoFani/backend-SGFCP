#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Eliminar tablas no usadas en SQLite (si existen)."""
import os
import sys

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app import create_app
from app.db import db

TABLES_TO_DROP = [
    "km_rate",
    "commission_percentage",
    "monthly_summary",
    "payroll_adjustments",
    "payroll_settings",
]


def table_exists(table_name: str) -> bool:
    result = db.session.execute(
        text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
        ),
        {"name": table_name},
    )
    return result.fetchone() is not None


def main():
    app = create_app()
    with app.app_context():
        # sqlite_sequence es una tabla interna de SQLite
        if table_exists("sqlite_sequence"):
            db.session.execute(text("DELETE FROM sqlite_sequence"))
            print("✅ sqlite_sequence limpiada")
        else:
            print("ℹ️ sqlite_sequence no existe")

        for table in TABLES_TO_DROP:
            if table_exists(table):
                db.session.execute(text(f"DROP TABLE {table}"))
                print(f"✅ Tabla {table} eliminada")
            else:
                print(f"ℹ️ Tabla {table} no existe")

        db.session.commit()
        print("✅ Limpieza completada")


if __name__ == '__main__':
    main()
