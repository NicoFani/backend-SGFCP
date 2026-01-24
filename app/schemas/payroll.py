"""Schemas para validación de datos de liquidación."""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class PayrollPeriodSchema(Schema):
    """Schema para período de liquidación."""
    id = fields.Int(dump_only=True)
    year = fields.Int(required=True, validate=validate.Range(min=2020, max=2100))
    month = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    has_trips_in_progress = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('end_date')
    def validate_end_date(self, value):
        """Validar que end_date sea posterior a start_date."""
        if 'start_date' in self.context and value <= self.context['start_date']:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")


class PayrollSummarySchema(Schema):
    """Schema para resumen de liquidación."""
    id = fields.Int(dump_only=True)
    period_id = fields.Int(required=True)
    driver_id = fields.Int(required=True)
    driver_commission_percentage = fields.Decimal(as_string=True, dump_only=True)
    driver_minimum_guaranteed = fields.Decimal(as_string=True, dump_only=True)
    commission_from_trips = fields.Decimal(as_string=True, dump_only=True)
    expenses_to_reimburse = fields.Decimal(as_string=True, dump_only=True)
    expenses_to_deduct = fields.Decimal(as_string=True, dump_only=True)
    guaranteed_minimum_applied = fields.Decimal(as_string=True, dump_only=True)
    advances_deducted = fields.Decimal(as_string=True, dump_only=True)
    other_items_total = fields.Decimal(as_string=True, dump_only=True)
    total_amount = fields.Decimal(as_string=True, dump_only=True)
    status = fields.Str(dump_only=True, validate=validate.OneOf([
        'calculation_pending', 'pending_approval', 'error', 'draft', 'approved'
    ]))
    error_message = fields.Str(allow_none=True, dump_only=True)
    is_auto_generated = fields.Bool(dump_only=True)
    export_format = fields.Str(dump_only=True)
    export_path = fields.Str(dump_only=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Campos del período (se agregan manualmente en la ruta)
    period_month = fields.Int(dump_only=True)
    period_year = fields.Int(dump_only=True)


class GeneratePayrollSchema(Schema):
    """
    Schema para generación de liquidaciones.
    
    Genera resúmenes para viajes finalizados. Los viajes en curso se incluirán
    automáticamente cuando se finalicen.
    """
    period_id = fields.Int(required=True)
    driver_ids = fields.List(fields.Int(), allow_none=True)  # None = todos los choferes
    is_manual = fields.Bool(missing=False)  # True si es generación manual


class PayrollDetailSchema(Schema):
    """Schema para detalle de liquidación."""
    id = fields.Int(dump_only=True)
    summary_id = fields.Int(dump_only=True)
    detail_type = fields.Str(dump_only=True)
    trip_id = fields.Int(allow_none=True, dump_only=True)
    expense_id = fields.Int(allow_none=True, dump_only=True)
    advance_id = fields.Int(allow_none=True, dump_only=True)
    adjustment_id = fields.Int(allow_none=True, dump_only=True)
    description = fields.Str(dump_only=True)
    amount = fields.Decimal(as_string=True, dump_only=True)
    calculation_data = fields.Str(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class PayrollAdjustmentSchema(Schema):
    """Schema para ajuste retroactivo."""
    id = fields.Int(dump_only=True)
    origin_period_id = fields.Int(required=True)
    driver_id = fields.Int(required=True)
    trip_id = fields.Int(allow_none=True)
    expense_id = fields.Int(allow_none=True)
    amount = fields.Decimal(as_string=True, required=True, places=2)
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    adjustment_type = fields.Str(
        required=True,
        validate=validate.OneOf(['manual', 'expense_post_close', 'trip_correction'])
    )
    applied_in_period_id = fields.Int(dump_only=True)
    is_applied = fields.Str(dump_only=True)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class PayrollSettingsSchema(Schema):
    """Schema para configuración de liquidación."""
    id = fields.Int(dump_only=True)
    guaranteed_minimum = fields.Decimal(
        as_string=True,
        required=True,
        places=2,
        validate=validate.Range(min=0)
    )
    default_commission_percentage = fields.Decimal(
        as_string=True,
        required=True,
        places=2,
        validate=validate.Range(min=0, max=100)
    )
    auto_generation_day = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=31)
    )
    effective_from = fields.DateTime(required=True)
    effective_until = fields.DateTime(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DriverCommissionHistorySchema(Schema):
    """Schema para historial de comisión del chofer."""
    id = fields.Int(dump_only=True)
    driver_id = fields.Int(required=True)
    commission_percentage = fields.Decimal(
        as_string=True,
        required=True,
        places=2,
        validate=validate.Range(min=0, max=100)
    )
    effective_from = fields.DateTime(required=True)
    effective_until = fields.DateTime(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class ExportPayrollSchema(Schema):
    """Schema para exportación de liquidación."""
    summary_id = fields.Int(required=True)
    format = fields.Str(
        required=True,
        validate=validate.OneOf(['excel', 'pdf'])
    )


class ApprovePayrollSchema(Schema):
    """Schema para aprobar liquidación."""
    summary_id = fields.Int(required=True)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))


class ClosePeriodSchema(Schema):
    """Schema para cerrar período."""
    period_id = fields.Int(required=True)
    force = fields.Bool(missing=False)  # Forzar cierre aunque haya viajes en curso


class MinimumGuaranteedHistorySchema(Schema):
    """Schema para histórico de mínimo garantizado."""
    id = fields.Int(dump_only=True)
    driver_id = fields.Int(required=True)
    minimum_guaranteed = fields.Decimal(
        as_string=True,
        required=True,
        places=2,
        validate=validate.Range(min=0)
    )
    effective_from = fields.DateTime(required=True)
    effective_until = fields.DateTime(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class PayrollOtherItemSchema(Schema):
    """Schema para otros conceptos de liquidación."""
    id = fields.Int(dump_only=True)
    driver_id = fields.Int(required=True)
    period_id = fields.Int(required=True)
    item_type = fields.Str(
        required=True,
        validate=validate.OneOf(['adjustment', 'bonus', 'extra_charge', 'fine_without_trip'])
    )
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    amount = fields.Decimal(as_string=True, required=True, places=2)
    date = fields.Date(required=False, dump_only=False, allow_none=True)
    reference = fields.Str(allow_none=True, validate=validate.Length(max=255))
    receipt_url = fields.Str(allow_none=True, validate=validate.Length(max=255))
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class RecalculateSummarySchema(Schema):
    """Schema para recalcular resumen."""
    summary_id = fields.Int(required=True)
