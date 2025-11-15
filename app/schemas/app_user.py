from marshmallow import Schema, fields, validate

class AppUserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    surname = fields.String(required=True, validate=validate.Length(max=50))
    is_admin = fields.Boolean(required=True)

class AppUserUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(max=50))
    surname = fields.String(validate=validate.Length(max=50))
    is_admin = fields.Boolean()
