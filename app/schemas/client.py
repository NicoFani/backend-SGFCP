from marshmallow import Schema, fields, validate

class ClientSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))

class ClientUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(max=50))
