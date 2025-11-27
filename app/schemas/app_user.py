from marshmallow import Schema, fields, validate

class AppUserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    surname = fields.String(required=True, validate=validate.Length(max=50))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))
    is_admin = fields.Boolean(required=True)
    is_active = fields.Boolean(dump_only=True)

class AppUserUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(max=50))
    surname = fields.String(validate=validate.Length(max=50))
    email = fields.Email(validate=validate.Length(max=120))
    is_admin = fields.Boolean()
    is_active = fields.Boolean()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class RegisterSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(max=50))
    surname = fields.String(required=True, validate=validate.Length(max=50))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(required=True, validate=validate.Length(min=6))
    is_admin = fields.Boolean(missing=False)
