"""Modelo para historizar el mínimo garantizado por chofer."""
from datetime import datetime
from app.models.base import db


class MinimumGuaranteedHistory(db.Model):
    """Historial de mínimo garantizado de un chofer."""
    
    __tablename__ = 'minimum_guaranteed_history'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    minimum_guaranteed = db.Column(db.Numeric(12, 2), nullable=False)
    
    effective_from = db.Column(db.DateTime, nullable=False)
    effective_until = db.Column(db.DateTime, nullable=True)  # NULL = vigente actualmente
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    driver = db.relationship("Driver", backref="minimum_guaranteed_history")
    
    def __repr__(self):
        return f'<MinimumGuaranteedHistory Driver:{self.driver_id} {self.minimum_guaranteed} from {self.effective_from}>'
