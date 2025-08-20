from .db import db

# Enums
from sqlalchemy.dialects.postgresql import ENUM

calculation_method_enum = ENUM('Porcentaje', 'KM Recorrido', name='calculation_method', create_type=False)
expense_type_enum = ENUM('Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje', name='expense_type', create_type=False)
toll_paid_by_enum = ENUM('Administrador', 'Chofer', name='toll_paid_by', create_type=False)
toll_type_enum = ENUM('Peaje de ruta', 'Tasa portuaria', 'Derecho de Ingreso a establecimiento', name='toll_type', create_type=False)
trip_state_enum = ENUM('Pendiente', 'En curso', 'Finalizado', name='trip_state', create_type=False)

class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    drivers = db.relationship('Driver', backref='app_user', lazy=True)
    advance_payments = db.relationship('AdvancePayment', backref='admin', lazy=True, foreign_keys='AdvancePayment.admin_id')

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
    advance_payments = db.relationship('AdvancePayment', backref='driver', lazy=True, foreign_keys='AdvancePayment.driver_id')
    driver_trucks = db.relationship('DriverTruck', backref='driver', lazy=True)
    trips = db.relationship('Trip', backref='driver', lazy=True)
    monthly_summaries = db.relationship('MonthlySummary', backref='driver', lazy=True)

class AdvancePayment(db.Model):
    __tablename__ = 'advance_payment'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    receipt = db.Column(db.String(75))

class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    trips = db.relationship('Trip', backref='client', lazy=True)

class CommissionPercentage(db.Model):
    __tablename__ = 'commission_percentage'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    percentage = db.Column(db.Float, nullable=False)

class DriverTruck(db.Model):
    __tablename__ = 'driver_truck'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)

class Truck(db.Model):
    __tablename__ = 'truck'
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(7), nullable=False)
    operational = db.Column(db.Boolean, nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    fabrication_year = db.Column(db.Integer, nullable=False)
    service_due_date = db.Column(db.Date, nullable=False)
    vtv_due_date = db.Column(db.Date, nullable=False)
    plate_due_date = db.Column(db.Date, nullable=False)
    driver_trucks = db.relationship('DriverTruck', backref='truck', lazy=True)

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id', ondelete='CASCADE'))
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

class KmRate(db.Model):
    __tablename__ = 'km_rate'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float, nullable=False)

class LoadOwner(db.Model):
    __tablename__ = 'load_owner'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    trips = db.relationship('Trip', backref='load_owner', lazy=True)

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

