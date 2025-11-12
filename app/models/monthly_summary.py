from .base import db, calculation_method_enum

class MonthlySummary(db.Model):
    __tablename__ = 'monthly_summary'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False)
    calculation_method = db.Column(calculation_method_enum, nullable=False)
    trips_counter = db.Column(db.Integer, nullable=False)
    trips_count = db.Column(db.Integer, nullable=False)
    km_traveled = db.Column(db.Float)
    total_tons = db.Column(db.Float, nullable=False)
    total_billed = db.Column(db.Float, nullable=False)
    total_commission = db.Column(db.Float, nullable=False)
    total_expenses = db.Column(db.Float, nullable=False)
    total_advance_payments = db.Column(db.Float, nullable=False)
    final_settlement = db.Column(db.Float, nullable=False)
    pdf_url = db.Column(db.String(75), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'month': self.month,
            'year': self.year,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'calculation_method': self.calculation_method,
            'trips_counter': self.trips_counter,
            'trips_count': self.trips_count,
            'km_traveled': self.km_traveled,
            'total_tons': self.total_tons,
            'total_billed': self.total_billed,
            'total_commission': self.total_commission,
            'total_expenses': self.total_expenses,
            'total_advance_payments': self.total_advance_payments,
            'final_settlement': self.final_settlement,
            'pdf_url': self.pdf_url
        }