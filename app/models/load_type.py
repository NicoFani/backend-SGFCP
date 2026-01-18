from .base import db

class LoadType(db.Model):
    __tablename__ = 'load_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    default_calculated_per_km = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relación con Trip
    trips = db.relationship('Trip', backref='load_type', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'default_calculated_per_km': self.default_calculated_per_km
        }
