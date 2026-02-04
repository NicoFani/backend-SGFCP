#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cambiar un resumen aprobado de marzo 2026 a pending_approval."""
import os
import sys
from datetime import datetime

# Agregar el directorio actual al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_period import PayrollPeriod
from app.models.base import db


def main():
    app = create_app()
    with app.app_context():
        period = PayrollPeriod.query.filter_by(year=2026, month=3).first()
        if not period:
            print("❌ No se encontró el período 03/2026")
            return

        summary = PayrollSummary.query.filter_by(
            period_id=period.id,
            status='approved'
        ).order_by(PayrollSummary.id.asc()).first()

        if not summary:
            print("❌ No hay resúmenes aprobados en 03/2026")
            return

        summary.status = 'pending_approval'
        summary.updated_at = datetime.now()
        db.session.commit()

        print(
            f"✅ Resumen {summary.id} cambiado a pending_approval "
            f"(chofer {summary.driver_id})"
        )


if __name__ == '__main__':
    main()
