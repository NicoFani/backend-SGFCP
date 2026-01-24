"""Modelo para resúmenes de liquidación por chofer."""
from datetime import datetime
from app.models.base import db


class PayrollSummary(db.Model):
    """Resumen de liquidación para un chofer en un período."""
    
    __tablename__ = 'payroll_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    
    # Comisión del chofer vigente al momento del cálculo
    driver_commission_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    
    # Mínimo garantizado vigente al momento del cálculo
    driver_minimum_guaranteed = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    
    # Totales calculados
    commission_from_trips = db.Column(db.Numeric(12, 2), default=0.0)
    expenses_to_reimburse = db.Column(db.Numeric(12, 2), default=0.0)
    expenses_to_deduct = db.Column(db.Numeric(12, 2), default=0.0)
    guaranteed_minimum_applied = db.Column(db.Numeric(12, 2), default=0.0)
    advances_deducted = db.Column(db.Numeric(12, 2), default=0.0)
    other_items_total = db.Column(db.Numeric(12, 2), default=0.0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Estados: calculation_pending, pending_approval, error, draft, approved
    status = db.Column(db.String(20), nullable=False, default='draft')
    error_message = db.Column(db.Text, nullable=True)  # Descripción del error si status = 'error'
    
    # Indicador de generación automática
    is_auto_generated = db.Column(db.Boolean, default=False)
    
    # Exportación
    export_format = db.Column(db.String(10), nullable=True)  # excel, pdf
    export_path = db.Column(db.String(255), nullable=True)
    
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    period = db.relationship("PayrollPeriod", backref="summaries")
    driver = db.relationship("Driver", backref="payroll_summaries")
    
    def __repr__(self):
        return f'<PayrollSummary Period:{self.period_id} Driver:{self.driver_id} Total:{self.total_amount}>'
