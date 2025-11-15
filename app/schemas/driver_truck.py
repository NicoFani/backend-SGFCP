from marshmallow import Schema, fields

class DriverTruckSchema(Schema):
    id = fields.Integer(dump_only=True)
    driver_id = fields.Integer(required=True)
    truck_id = fields.Integer(required=True)
    date = fields.Date(required=True)

class DriverTruckUpdateSchema(Schema):
    driver_id = fields.Integer()
    truck_id = fields.Integer()
    date = fields.Date()
