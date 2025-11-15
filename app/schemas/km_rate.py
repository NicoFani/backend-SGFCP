from marshmallow import Schema, fields, validate

class KmRateSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    rate = fields.Float(required=True, validate=validate.Range(min=0))

class KmRateUpdateSchema(Schema):
    date = fields.Date()
    rate = fields.Float(validate=validate.Range(min=0))
