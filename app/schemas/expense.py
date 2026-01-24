# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, validate

class ExpenseSchema(Schema):
    trip_id = fields.Integer(allow_none=True)
    driver_id = fields.Integer(required=True)
    expense_type = fields.String(required=True, validate=validate.OneOf(['Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje']))
    date = fields.Date(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.String(validate=validate.Length(max=75))
    receipt_url = fields.String(validate=validate.Length(max=75))
    fine_municipality = fields.String(validate=validate.Length(max=50))
    repair_type = fields.String(validate=validate.Length(max=50))
    fuel_liters = fields.Float(validate=validate.Range(min=0))
    toll_type = fields.String(validate=validate.OneOf(['Peaje de ruta', 'Tasa portuaria', 'Derecho de Ingreso a establecimiento']))
    paid_by_admin = fields.Boolean(allow_none=True)  # Para Reparaciones y Peajes
    toll_port_fee_name = fields.String(validate=validate.Length(max=75))

class ExpenseUpdateSchema(Schema):
    trip_id = fields.Integer(allow_none=True)
    driver_id = fields.Integer()
    expense_type = fields.String(validate=validate.OneOf(['Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje']))
    date = fields.Date()
    amount = fields.Float(validate=validate.Range(min=0))
    description = fields.String(validate=validate.Length(max=75))
    receipt_url = fields.String(validate=validate.Length(max=75))
    fine_municipality = fields.String(validate=validate.Length(max=50))
    repair_type = fields.String(validate=validate.Length(max=50))
    fuel_liters = fields.Float(validate=validate.Range(min=0))
    toll_type = fields.String(validate=validate.OneOf(['Peaje de ruta', 'Tasa portuaria', 'Derecho de Ingreso a establecimiento']))
    paid_by_admin = fields.Boolean(allow_none=True)  # Para Reparaciones y Peajes
    toll_port_fee_name = fields.String(validate=validate.Length(max=75))