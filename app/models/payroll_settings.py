"""Modelo para configuración global de liquidación."""
from datetime import datetime
from app.models.base import db


class PayrollSettings(db.Model):
    """Configuración global del sistema de liquidación."""
    
    __tablename__ = 'payroll_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    guaranteed_minimum = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    default_commission_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=18.0)
    auto_generation_day = db.Column(db.Integer, nullable=False, default=31)  # Día del mes
    
    effective_from = db.Column(db.DateTime, nullable=False)
    effective_until = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PayrollSettings Min:{self.guaranteed_minimum} Commission:{self.default_commission_percentage}%>'
