from marshmallow import Schema, fields, validate

class AdvancePaymentSchema(Schema):
    id = fields.Integer(dump_only=True)
    admin_id = fields.Integer(required=True)
    driver_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    receipt = fields.String(validate=validate.Length(max=75), allow_none=True)

class AdvancePaymentUpdateSchema(Schema):
    admin_id = fields.Integer()
    driver_id = fields.Integer()
    date = fields.Date()
    amount = fields.Float(validate=validate.Range(min=0))
    receipt = fields.String(validate=validate.Length(max=75), allow_none=True)
