from .base import db

class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    drivers = db.relationship('Driver', backref='app_user', lazy=True)
    advance_payments = db.relationship('AdvancePayment', backref='admin', lazy=True, foreign_keys='AdvancePayment.admin_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'is_admin': self.is_admin
        }