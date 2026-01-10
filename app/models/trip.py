from .base import db, trip_state_enum, document_type_enum, trip_drivers

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
    rate_per_ton = db.Column(db.Float)
    km_rate = db.Column(db.Float)
    calculation_type = db.Column(db.String(20))  # by_tonnage, by_km, both
    fuel_on_client = db.Column(db.Boolean, default=False)
    fuel_liters = db.Column(db.Float)
    state_id = db.Column(trip_state_enum, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    load_owner_id = db.Column(db.Integer, db.ForeignKey('load_owner.id'))
    
    # Relación muchos-a-muchos con Driver
    drivers = db.relationship('Driver', secondary=trip_drivers, backref='trips_assigned', lazy=True)
    
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
            'rate_per_ton': self.rate_per_ton,
            'km_rate': self.km_rate,
            'calculation_type': self.calculation_type,
            'fuel_on_client': self.fuel_on_client,
            'fuel_liters': self.fuel_liters,
            'state_id': self.state_id,
            'client_id': self.client_id,
            'load_owner_id': self.load_owner_id,
            'drivers': [{'id': d.id, 'name': d.user.name, 'surname': d.user.surname} for d in self.drivers]
        }