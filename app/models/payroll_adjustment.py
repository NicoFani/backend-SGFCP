"""DEPRECATED: Este modelo ya no se usa.
Ahora se usa PayrollOtherItem para ajustes, bonificaciones, cargos extra y multas sin viaje."""
from datetime import datetime
from app.models.base import db


class PayrollAdjustment(db.Model):
    """Ajuste retroactivo a un período cerrado."""
    
    __tablename__ = 'payroll_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    origin_period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=False)  # Período ajustado
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    
    # Referencias opcionales al origen del ajuste
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=True)
    
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # Puede ser positivo o negativo
    description = db.Column(db.Text, nullable=False)
    adjustment_type = db.Column(db.String(30), nullable=False)  # manual, expense_post_close, trip_correction
    
    # Período donde se aplicará el ajuste (normalmente el siguiente abierto)
    applied_in_period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=True)
    is_applied = db.Column(db.String(20), default='pending')  # pending, applied
    
    created_by = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    origin_period = db.relationship("PayrollPeriod", foreign_keys=[origin_period_id], backref="adjustments_origin")
    applied_period = db.relationship("PayrollPeriod", foreign_keys=[applied_in_period_id], backref="adjustments_applied")
    driver = db.relationship("Driver", backref="payroll_adjustments")
    trip = db.relationship("Trip", backref="payroll_adjustments")
    expense = db.relationship("Expense", backref="payroll_adjustments")
    creator = db.relationship("AppUser", backref="created_adjustments")
    
    def __repr__(self):
        return f'<PayrollAdjustment Period:{self.origin_period_id} Driver:{self.driver_id} Amount:{self.amount}>'
