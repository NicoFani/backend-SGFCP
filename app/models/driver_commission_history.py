"""Modelo para historizar porcentaje de comisión del chofer."""
from datetime import datetime
from app.models.base import db


class DriverCommissionHistory(db.Model):
    """Historial de porcentajes de comisión de un chofer."""
    
    __tablename__ = 'driver_commission_history'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    commission_percentage = db.Column(db.Numeric(5, 4), nullable=False)  # Decimal entre 0 y 1 (ej: 0.18 = 18%)
    
    effective_from = db.Column(db.DateTime, nullable=False)
    effective_until = db.Column(db.DateTime, nullable=True)  # NULL = vigente actualmente
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    driver = db.relationship("Driver", backref="commission_history")
    
    def __repr__(self):
        return f'<DriverCommissionHistory Driver:{self.driver_id} {self.commission_percentage}% from {self.effective_from}>'
