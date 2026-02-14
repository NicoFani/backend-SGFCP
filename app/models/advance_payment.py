from .base import db

class AdvancePayment(db.Model):
    __tablename__ = 'advance_payment'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    receipt = db.Column(db.String(255))  # URL de Supabase Storage

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'driver_id': self.driver_id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'receipt': self.receipt
        }