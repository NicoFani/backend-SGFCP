from marshmallow import Schema, fields, validate

class LoadTypeSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(max=100))
    default_calculated_per_km = fields.Boolean(required=True)

class LoadTypeUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(max=100))
    default_calculated_per_km = fields.Boolean()
