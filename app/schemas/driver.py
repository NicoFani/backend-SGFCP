from marshmallow import Schema, fields, validate
from marshmallow.exceptions import ValidationError

class DriverSchema(Schema):
    id = fields.Integer(required=True)
    dni = fields.Integer(required=True, validate=validate.Range(min=1000000, max=99999999))
    cuil = fields.String(required=True, validate=validate.Length(equal=11))
    phone_number = fields.String(required=True, validate=validate.Length(max=20))
    cbu = fields.String(required=True, validate=validate.Length(equal=22))
    active = fields.Boolean(missing=True)
    enrollment_date = fields.Date(required=True)
    termination_date = fields.Date(allow_none=True)
    driver_license_due_date = fields.Date(required=True)
    medical_exam_due_date = fields.Date(required=True)

class DriverUpdateSchema(Schema):
    dni = fields.Integer(validate=validate.Range(min=1000000, max=99999999))
    cuil = fields.String(validate=validate.Length(equal=11))
    phone_number = fields.String(validate=validate.Length(max=20))
    cbu = fields.String(validate=validate.Length(equal=22))
    active = fields.Boolean()
    enrollment_date = fields.Date()
    termination_date = fields.Date(allow_none=True)
    driver_license_due_date = fields.Date()
    medical_exam_due_date = fields.Date()