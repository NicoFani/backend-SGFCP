# -*- coding: utf-8 -*-
from ..db import db
from sqlalchemy.dialects.postgresql import ENUM

# Enums
calculation_method_enum = ENUM('Porcentaje', 'KM Recorrido', name='calculation_method', create_type=False)
expense_type_enum = ENUM('Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje', name='expense_type', create_type=False)
toll_paid_by_enum = ENUM('Contador', 'Chofer', name='toll_paid_by', create_type=False)
toll_type_enum = ENUM('Peaje de ruta', 'Tasa portuaria', 'Derecho de Ingreso a establecimiento', name='toll_type', create_type=False)
trip_state_enum = ENUM('Pendiente', 'En curso', 'Finalizado', name='trip_state', create_type=False)
document_type_enum = ENUM('CTG', 'Remito', name='document_type', create_type=False)

# Tabla asociativa para relación muchos-a-muchos Trip-Driver
trip_drivers = db.Table('trip_drivers',
    db.Column('trip_id', db.Integer, db.ForeignKey('trip.id', ondelete='CASCADE'), primary_key=True),
    db.Column('driver_id', db.Integer, db.ForeignKey('driver.id', ondelete='CASCADE'), primary_key=True)
)