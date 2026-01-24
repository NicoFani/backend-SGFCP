from marshmallow import Schema, fields, validate, validates, ValidationError

class TripSchema(Schema):
    origin = fields.String(required=True, validate=validate.Length(max=100))
    origin_description = fields.String(allow_none=True, validate=validate.Length(max=255))
    destination = fields.String(required=True, validate=validate.Length(max=100))
    destination_description = fields.String(allow_none=True, validate=validate.Length(max=255))
    document_type = fields.String(allow_none=True, validate=validate.OneOf(['CTG', 'Remito']))
    document_number = fields.String(allow_none=True, validate=validate.Length(max=20))
    estimated_kms = fields.Float(allow_none=True, validate=validate.Range(min=0))
    start_date = fields.Date(required=True)
    end_date = fields.Date(allow_none=True)
    load_weight_on_load = fields.Float(allow_none=True, validate=validate.Range(min=0))
    load_weight_on_unload = fields.Float(allow_none=True, validate=validate.Range(min=0))
    calculated_per_km = fields.Boolean(allow_none=True)
    rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    fuel_on_client = fields.Boolean(allow_none=True)
    fuel_liters = fields.Float(allow_none=True, validate=validate.Range(min=0))
    state_id = fields.String(required=True, validate=validate.OneOf(['Pendiente', 'En curso', 'Finalizado']))
    client_id = fields.Integer(required=True)
    load_owner_id = fields.Integer(allow_none=True)
    load_type_id = fields.Integer(allow_none=True)
    driver_id = fields.Integer(required=True)
    client_advance_payment = fields.Float(allow_none=True, validate=validate.Range(min=0))

    @validates('document_number')
    def validate_document_number(self, value):
        if not value:
            return
        # Validar según tipo de documento
        if 'document_type' in self.context:
            doc_type = self.context['document_type']
            if doc_type == 'CTG' and len(value) != 11:
                raise ValidationError('CTG debe tener 11 dígitos')
            elif doc_type == 'Remito' and len(value) != 13:  # 5 + 8
                raise ValidationError('Remito debe tener 5 dígitos de punto de venta + 8 de número')

class TripUpdateSchema(Schema):
    origin = fields.String(validate=validate.Length(max=100))
    origin_description = fields.String(allow_none=True, validate=validate.Length(max=255))
    destination = fields.String(validate=validate.Length(max=100))
    destination_description = fields.String(allow_none=True, validate=validate.Length(max=255))
    document_type = fields.String(allow_none=True, validate=validate.OneOf(['CTG', 'Remito']))
    document_number = fields.String(allow_none=True, validate=validate.Length(max=20))
    estimated_kms = fields.Float(allow_none=True, validate=validate.Range(min=0))
    start_date = fields.Date()
    end_date = fields.Date(allow_none=True)
    load_weight_on_load = fields.Float(allow_none=True, validate=validate.Range(min=0))
    load_weight_on_unload = fields.Float(allow_none=True, validate=validate.Range(min=0))
    calculated_per_km = fields.Boolean()
    rate = fields.Float(allow_none=True, validate=validate.Range(min=0))
    fuel_on_client = fields.Boolean(allow_none=True)
    fuel_liters = fields.Float(allow_none=True, validate=validate.Range(min=0))
    state_id = fields.String(validate=validate.OneOf(['Pendiente', 'En curso', 'Finalizado']))
    client_id = fields.Integer()
    load_owner_id = fields.Integer(allow_none=True)
    load_type_id = fields.Integer()
    driver_id = fields.Integer()
    client_advance_payment = fields.Float(allow_none=True, validate=validate.Range(min=0))