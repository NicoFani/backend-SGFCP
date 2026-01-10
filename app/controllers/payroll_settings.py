"""Controlador para configuración de liquidación."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, or_
from app.models.base import db
from app.models.payroll_settings import PayrollSettings


class PayrollSettingsController:
    """Controlador para configuración de liquidación."""
    
    @staticmethod
    def get_current_settings():
        """Obtener la configuración vigente actual."""
        now = datetime.utcnow()
        
        settings = PayrollSettings.query.filter(
            and_(
                PayrollSettings.effective_from <= now,
                or_(
                    PayrollSettings.effective_until.is_(None),
                    PayrollSettings.effective_until >= now
                )
            )
        ).order_by(PayrollSettings.effective_from.desc()).first()
        
        if not settings:
            # Crear configuración por defecto
            settings = PayrollSettingsController.create_settings(
                guaranteed_minimum=0.0,
                default_commission_percentage=18.0,
                auto_generation_day=31
            )
        
        return settings
    
    @staticmethod
    def create_settings(guaranteed_minimum, default_commission_percentage, 
                       auto_generation_day, effective_from=None):
        """Crear nueva configuración."""
        if effective_from is None:
            effective_from = datetime.utcnow()
        
        # Cerrar la configuración anterior
        previous_settings = PayrollSettings.query.filter(
            PayrollSettings.effective_until.is_(None)
        ).all()
        
        for prev in previous_settings:
            prev.effective_until = effective_from
        
        # Crear nueva configuración
        settings = PayrollSettings(
            guaranteed_minimum=Decimal(str(guaranteed_minimum)),
            default_commission_percentage=Decimal(str(default_commission_percentage)),
            auto_generation_day=auto_generation_day,
            effective_from=effective_from
        )
        
        db.session.add(settings)
        db.session.commit()
        
        return settings
    
    @staticmethod
    def update_settings(guaranteed_minimum=None, default_commission_percentage=None,
                       auto_generation_day=None):
        """Actualizar la configuración actual (crea un nuevo registro histórico)."""
        current = PayrollSettingsController.get_current_settings()
        
        # Usar valores actuales si no se especifican nuevos
        new_guaranteed_minimum = guaranteed_minimum if guaranteed_minimum is not None else current.guaranteed_minimum
        new_commission_pct = default_commission_percentage if default_commission_percentage is not None else current.default_commission_percentage
        new_generation_day = auto_generation_day if auto_generation_day is not None else current.auto_generation_day
        
        # Crear nueva configuración con fecha efectiva actual
        new_settings = PayrollSettingsController.create_settings(
            guaranteed_minimum=new_guaranteed_minimum,
            default_commission_percentage=new_commission_pct,
            auto_generation_day=new_generation_day,
            effective_from=datetime.utcnow()
        )
        
        return new_settings
    
    @staticmethod
    def get_settings_history(page=1, per_page=20):
        """Obtener historial de configuraciones."""
        query = PayrollSettings.query.order_by(
            PayrollSettings.effective_from.desc()
        )
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_settings_at_date(reference_date):
        """Obtener la configuración vigente en una fecha específica."""
        settings = PayrollSettings.query.filter(
            and_(
                PayrollSettings.effective_from <= reference_date,
                or_(
                    PayrollSettings.effective_until.is_(None),
                    PayrollSettings.effective_until >= reference_date
                )
            )
        ).order_by(PayrollSettings.effective_from.desc()).first()
        
        if not settings:
            # Si no hay configuración para esa fecha, usar la actual
            settings = PayrollSettingsController.get_current_settings()
        
        return settings
