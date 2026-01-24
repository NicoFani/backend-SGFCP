"""Modelo para otros conceptos de liquidación (ajustes, bonificaciones, cargos extra, multas sin viaje)."""
from datetime import datetime
from app.models.base import db


class PayrollOtherItem(db.Model):
    """Otros conceptos que afectan la liquidación del chofer."""
    
    __tablename__ = 'payroll_other_items'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('payroll_periods.id'), nullable=False)
    
    # Tipo: adjustment, bonus, extra_charge, fine_without_trip
    item_type = db.Column(db.String(30), nullable=False)
    
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # Puede ser positivo o negativo
    date = db.Column(db.Date, nullable=False)
    
    # Referencia opcional (por ejemplo, si es una multa puede referenciar algo)
    reference = db.Column(db.String(255), nullable=True)
    receipt_url = db.Column(db.String(255), nullable=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    driver = db.relationship("Driver", backref="other_items")
    period = db.relationship("PayrollPeriod", backref="other_items")
    creator = db.relationship("AppUser", backref="created_other_items")
    
    def __repr__(self):
        return f'<PayrollOtherItem {self.item_type} Driver:{self.driver_id} Amount:{self.amount}>'
