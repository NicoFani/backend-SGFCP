from .base import db

class DriverTruck(db.Model):
    __tablename__ = 'driver_truck'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'truck_id': self.truck_id,
            'date': self.date.isoformat() if self.date else None
        }