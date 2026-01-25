from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date

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

    @validates('start_date')
    def validate_start_date(self, value):
        """Valida que la fecha de inicio no sea anterior a la fecha actual"""
        if value and value < date.today():
            raise ValidationError('La fecha de inicio no puede ser anterior al día actual')

    @validates('load_weight_on_unload')
    def validate_unload_weight(self, value):
        """Valida que el peso de descarga no sea mayor al peso de carga"""
        if value is not None and 'load_weight_on_load' in self.context:
            load_weight = self.context['load_weight_on_load']
            if load_weight is not None and value > load_weight:
                raise ValidationError('El peso de descarga no puede ser mayor al peso de carga')

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