# -*- coding: utf-8 -*-
from ..db import db
from sqlalchemy.dialects.postgresql import ENUM

# Enums
calculation_method_enum = ENUM('Porcentaje', 'KM Recorrido', name='calculation_method', create_type=False)
expense_type_enum = ENUM('Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje', name='expense_type', create_type=False)
toll_paid_by_enum = ENUM('Administrador', 'Chofer', name='toll_paid_by', create_type=False)
toll_type_enum = ENUM('Peaje de ruta', 'Tasa portuaria', 'Derecho de Ingreso a establecimiento', name='toll_type', create_type=False)
trip_state_enum = ENUM('Pendiente', 'En curso', 'Finalizado', name='trip_state', create_type=False)