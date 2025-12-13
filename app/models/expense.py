from .base import db, expense_type_enum, toll_type_enum, toll_paid_by_enum

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id', ondelete='SET NULL'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    expense_type = db.Column(expense_type_enum, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(75))
    receipt_url = db.Column(db.String(75))
    fine_municipality = db.Column(db.String(50))
    repair_type = db.Column(db.String(50))
    fuel_liters = db.Column(db.Float)
    toll_type = db.Column(toll_type_enum)
    toll_paid_by = db.Column(toll_paid_by_enum)
    toll_port_fee_name = db.Column(db.String(75))

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'driver_id': self.driver_id,
            'expense_type': self.expense_type,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'description': self.description,
            'receipt_url': self.receipt_url,
            'fine_municipality': self.fine_municipality,
            'repair_type': self.repair_type,
            'fuel_liters': self.fuel_liters,
            'toll_type': self.toll_type,
            'toll_paid_by': self.toll_paid_by,
            'toll_port_fee_name': self.toll_port_fee_name
        }