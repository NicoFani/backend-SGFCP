"""DEPRECATED: Este modelo ya no se usa. 
La comisión ahora se maneja por chofer en DriverCommissionHistory."""
from .base import db

class CommissionPercentage(db.Model):
    __tablename__ = 'commission_percentage'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    percentage = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'percentage': self.percentage
        }