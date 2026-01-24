"""Modelo para períodos de liquidación de sueldos."""
from datetime import datetime
from app.models.base import db


class PayrollPeriod(db.Model):
    """Período de liquidación mensual."""
    
    __tablename__ = 'payroll_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    has_trips_in_progress = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PayrollPeriod {self.year}-{self.month:02d} ({self.status})>'
