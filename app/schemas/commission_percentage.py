from marshmallow import Schema, fields, validate

class CommissionPercentageSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    percentage = fields.Float(required=True, validate=validate.Range(min=0, max=100))

class CommissionPercentageUpdateSchema(Schema):
    date = fields.Date()
    percentage = fields.Float(validate=validate.Range(min=0, max=100))
