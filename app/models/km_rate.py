"""DEPRECATED: Este modelo ya no se usa.
La tarifa ahora se carga directamente en cada viaje (campo 'rate')."""
from .base import db

class KmRate(db.Model):
    __tablename__ = 'km_rate'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'rate': self.rate
        }