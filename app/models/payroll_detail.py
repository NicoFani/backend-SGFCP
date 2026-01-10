"""Modelo para detalle de cálculo de liquidación."""
from datetime import datetime
from app.models.base import db


class PayrollDetail(db.Model):
    """Detalle del cálculo de liquidación por viaje o concepto."""
    
    __tablename__ = 'payroll_details'
    
    id = db.Column(db.Integer, primary_key=True)
    summary_id = db.Column(db.Integer, db.ForeignKey('payroll_summaries.id'), nullable=False)
    
    # Tipo de detalle: trip_commission, expense_reimburse, expense_deduct, advance, adjustment
    detail_type = db.Column(db.String(30), nullable=False)
    
    # Referencias opcionales
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=True)
    advance_id = db.Column(db.Integer, db.ForeignKey('advance_payment.id'), nullable=True)
    adjustment_id = db.Column(db.Integer, db.ForeignKey('payroll_adjustments.id'), nullable=True)
    
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    calculation_data = db.Column(db.Text, nullable=True)  # JSON con detalles del cálculo
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    summary = db.relationship("PayrollSummary", backref="details")
    trip = db.relationship("Trip", backref="payroll_details")
    expense = db.relationship("Expense", backref="payroll_details")
    advance = db.relationship("AdvancePayment", backref="payroll_details")
    
    def __repr__(self):
        return f'<PayrollDetail {self.detail_type}: {self.amount}>'
