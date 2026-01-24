from .base import db, trip_state_enum, document_type_enum

class Trip(db.Model):
    __tablename__ = 'trip'
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False)
    origin_description = db.Column(db.String(255))
    destination = db.Column(db.String(100), nullable=False)
    destination_description = db.Column(db.String(255))
    document_type = db.Column(document_type_enum)
    document_number = db.Column(db.String(20))
    estimated_kms = db.Column(db.Float)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    load_weight_on_load = db.Column(db.Float)
    load_weight_on_unload = db.Column(db.Float)
    calculated_per_km = db.Column(db.Boolean, nullable=False, default=False)
    rate = db.Column(db.Float)
    fuel_on_client = db.Column(db.Boolean, default=False)
    fuel_liters = db.Column(db.Float)
    state_id = db.Column(trip_state_enum, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    load_owner_id = db.Column(db.Integer, db.ForeignKey('load_owner.id'))
    load_type_id = db.Column(db.Integer, db.ForeignKey('load_type.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    client_advance_payment = db.Column(db.Float, default=0.0)
    
    # Relación uno-a-uno con Driver
    driver = db.relationship('Driver', backref='trips', lazy=True)
    
    # Relaciones
    expenses = db.relationship('Expense', backref='trip', lazy=True)

    
    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'origin_description': self.origin_description,
            'destination': self.destination,
            'destination_description': self.destination_description,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'estimated_kms': self.estimated_kms,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'load_weight_on_load': self.load_weight_on_load,
            'load_weight_on_unload': self.load_weight_on_unload,
            'calculated_per_km': self.calculated_per_km,
            'rate': self.rate,
            'fuel_on_client': self.fuel_on_client,
            'fuel_liters': self.fuel_liters,
            'client_advance_payment': self.client_advance_payment,
            'state_id': self.state_id,
            'client_id': self.client_id,
            'load_owner_id': self.load_owner_id,
            'load_type_id': self.load_type_id,
            'load_type': self.load_type.to_dict() if self.load_type else None,
            'driver_id': self.driver_id,
            'driver': {'id': self.driver.id, 'name': self.driver.user.name, 'surname': self.driver.user.surname} if self.driver else None
        }