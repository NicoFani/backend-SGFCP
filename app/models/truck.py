from .base import db

class Truck(db.Model):
    __tablename__ = 'truck'
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(7), nullable=False)
    operational = db.Column(db.Boolean, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    fabrication_year = db.Column(db.Integer, nullable=False)
    service_due_date = db.Column(db.Date, nullable=False)
    vtv_due_date = db.Column(db.Date, nullable=False)
    plate_due_date = db.Column(db.Date, nullable=False)
    driver_trucks = db.relationship('DriverTruck', backref='truck', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'plate': self.plate,
            'operational': self.operational,
            'brand': self.brand,
            'model_name': self.model_name,
            'fabrication_year': self.fabrication_year,
            'service_due_date': self.service_due_date.isoformat() if self.service_due_date else None,
            'vtv_due_date': self.vtv_due_date.isoformat() if self.vtv_due_date else None,
            'plate_due_date': self.plate_due_date.isoformat() if self.plate_due_date else None
        }