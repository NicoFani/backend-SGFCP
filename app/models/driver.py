from .base import db
from sqlalchemy import desc

class Driver(db.Model):
    __tablename__ = 'driver'
    id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), primary_key=True)
    dni = db.Column(db.Integer, nullable=False)
    cuil = db.Column(db.String(11), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    cbu = db.Column(db.String(22), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date)
    driver_license_due_date = db.Column(db.Date, nullable=False)
    medical_exam_due_date = db.Column(db.Date, nullable=False)
    
    # Relationships
    user = db.relationship('AppUser', backref='driver_profile', lazy=True, foreign_keys=[id])
    advance_payments = db.relationship('AdvancePayment', backref='driver', lazy=True, foreign_keys='AdvancePayment.driver_id')
    driver_trucks = db.relationship('DriverTruck', backref='driver', lazy=True)
    monthly_summaries = db.relationship('MonthlySummary', backref='driver', lazy=True)

    def get_current_truck(self):
        """Obtiene el camión actual del chofer (el más reciente por fecha)"""
        from .driver_truck import DriverTruck
        from .truck import Truck
        
        # Obtener la asignación más reciente
        assignment = DriverTruck.query.filter_by(driver_id=self.id).order_by(desc(DriverTruck.date)).first()
        
        if not assignment:
            return None
        
        # Obtener el camión
        truck = Truck.query.get(assignment.truck_id)
        return truck.to_dict() if truck else None

    def to_dict(self):
        driver_dict = {
            'id': self.id,
            'dni': self.dni,
            'cuil': self.cuil,
            'phone_number': self.phone_number,
            'cbu': self.cbu,
            'active': self.active,
            'commission': self.commission,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'termination_date': self.termination_date.isoformat() if self.termination_date else None,
            'driver_license_due_date': self.driver_license_due_date.isoformat() if self.driver_license_due_date else None,
            'medical_exam_due_date': self.medical_exam_due_date.isoformat() if self.medical_exam_due_date else None
        }
        
        # Agregar información del usuario si existe
        if self.user:
            driver_dict['name'] = self.user.name
            driver_dict['surname'] = self.user.surname
            driver_dict['email'] = self.user.email
        
        # Agregar camión actual
        current_truck = self.get_current_truck()
        if current_truck:
            driver_dict['current_truck'] = current_truck
        
        return driver_dict