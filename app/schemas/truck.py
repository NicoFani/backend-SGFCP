from marshmallow import Schema, fields, validate

class TruckSchema(Schema):
    plate = fields.String(required=True, validate=validate.Length(max=7))
    operational = fields.Boolean(required=True)
    brand = fields.String(required=True, validate=validate.Length(max=50))
    model_name = fields.String(required=True, validate=validate.Length(max=50))
    fabrication_year = fields.Integer(required=True, validate=validate.Range(min=1900, max=2030))
    service_due_date = fields.Date(required=True)
    vtv_due_date = fields.Date(required=True)
    plate_due_date = fields.Date(required=True)

class TruckUpdateSchema(Schema):
    plate = fields.String(validate=validate.Length(max=7))
    operational = fields.Boolean()
    brand = fields.String(validate=validate.Length(max=50))
    model_name = fields.String(validate=validate.Length(max=50))
    fabrication_year = fields.Integer(validate=validate.Range(min=1900, max=2030))
    service_due_date = fields.Date()
    vtv_due_date = fields.Date()
    plate_due_date = fields.Date()