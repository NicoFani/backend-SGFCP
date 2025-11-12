from .base import db, trip_state_enum

class Trip(db.Model):
    __tablename__ = 'trip'
    id = db.Column(db.Integer, primary_key=True)
    document_number = db.Column(db.Integer)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    estimated_kms = db.Column(db.Float)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    load_weight_on_load = db.Column(db.Float)
    load_weight_on_unload = db.Column(db.Float)
    rate_per_ton = db.Column(db.Float)
    fuel_on_client = db.Column(db.Boolean)
    client_advance_payment = db.Column(db.Float)
    state_id = db.Column(trip_state_enum, nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    load_owner_id = db.Column(db.Integer, db.ForeignKey('load_owner.id'), nullable=False)
    expenses = db.relationship('Expense', backref='trip', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'document_number': self.document_number,
            'origin': self.origin,
            'destination': self.destination,
            'estimated_kms': self.estimated_kms,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'load_weight_on_load': self.load_weight_on_load,
            'load_weight_on_unload': self.load_weight_on_unload,
            'rate_per_ton': self.rate_per_ton,
            'fuel_on_client': self.fuel_on_client,
            'client_advance_payment': self.client_advance_payment,
            'state_id': self.state_id,
            'driver_id': self.driver_id,
            'client_id': self.client_id,
            'load_owner_id': self.load_owner_id
        }