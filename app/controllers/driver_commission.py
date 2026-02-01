"""Controlador para gestión del historial de comisión de choferes."""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_
from app.models.base import db
from app.models.driver_commission_history import DriverCommissionHistory
from app.models.driver import Driver


class DriverCommissionController:
    """Controlador para historial de comisiones de choferes."""
    
    @staticmethod
    def set_driver_commission(driver_id, commission_percentage, effective_from=None):
        """Establecer el porcentaje de comisión de un chofer."""
        # Validar chofer
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError("Chofer no encontrado")
        
        # Validar porcentaje
        if commission_percentage < 0 or commission_percentage > 100:
            raise ValueError("El porcentaje de comisión debe estar entre 0 y 100")
        
        # Buscar la comisión anterior más reciente del chofer
        previous_commission = DriverCommissionHistory.query.filter_by(
            driver_id=driver_id
        ).order_by(DriverCommissionHistory.effective_from.desc()).first()
        
        # Determinar effective_from y created_at para la nueva comisión
        if previous_commission:
            # Si hay comisión anterior, la nueva comienza el día siguiente al fin de la anterior
            if previous_commission.effective_until:
                # Si la anterior tiene fecha de fin, usar el día siguiente
                new_effective_from = previous_commission.effective_until + timedelta(days=1)
            else:
                # Si la anterior no tiene fecha de fin (está abierta), cerrarla con la fecha actual
                if effective_from is None:
                    effective_from = datetime.utcnow()
                # Cerrar la comisión anterior un día antes de la nueva
                previous_commission.effective_until = effective_from - timedelta(days=1)
                new_effective_from = effective_from
        else:
            # Si no hay comisión anterior, usar la fecha proporcionada o la actual
            if effective_from is None:
                new_effective_from = datetime.utcnow()
            else:
                new_effective_from = effective_from
        
        # created_at debe ser igual a effective_from
        created_at = new_effective_from
        
        # Crear nuevo registro
        commission_record = DriverCommissionHistory(
            driver_id=driver_id,
            commission_percentage=Decimal(str(commission_percentage)),
            effective_from=new_effective_from,
            created_at=created_at
        )
        
        db.session.add(commission_record)
        db.session.commit()
        
        return commission_record
    
    @staticmethod
    def get_driver_commission_at_date(driver_id, reference_date):
        """Obtener el porcentaje de comisión vigente en una fecha."""
        commission_record = DriverCommissionHistory.query.filter(
            and_(
                DriverCommissionHistory.driver_id == driver_id,
                DriverCommissionHistory.effective_from <= reference_date,
                or_(
                    DriverCommissionHistory.effective_until.is_(None),
                    DriverCommissionHistory.effective_until >= reference_date
                )
            )
        ).order_by(DriverCommissionHistory.effective_from.desc()).first()
        
        if commission_record:
            return commission_record.commission_percentage
        
        # Si no hay registro, usar el porcentaje por defecto del sistema
        from app.controllers.payroll_settings import PayrollSettingsController
        settings = PayrollSettingsController.get_current_settings()
        return settings.default_commission_percentage
    
    @staticmethod
    def get_driver_current_commission(driver_id):
        """Obtener el porcentaje de comisión actual del chofer."""
        return DriverCommissionController.get_driver_commission_at_date(
            driver_id, datetime.utcnow()
        )
    
    @staticmethod
    def get_driver_commission_history(driver_id):
        """Obtener el historial completo de comisiones de un chofer."""
        history = DriverCommissionHistory.query.filter_by(
            driver_id=driver_id
        ).order_by(DriverCommissionHistory.effective_from.desc()).all()
        
        return history
    
    @staticmethod
    def initialize_driver_commission(driver_id, commission_percentage=None):
        """Inicializar la comisión de un chofer nuevo."""
        # Verificar si ya tiene registros
        existing = DriverCommissionHistory.query.filter_by(driver_id=driver_id).first()
        if existing:
            raise ValueError("El chofer ya tiene un historial de comisiones")
        
        # Si no se especifica porcentaje, usar el por defecto
        if commission_percentage is None:
            from app.controllers.payroll_settings import PayrollSettingsController
            settings = PayrollSettingsController.get_current_settings()
            commission_percentage = settings.default_commission_percentage
        
        return DriverCommissionController.set_driver_commission(
            driver_id, commission_percentage
        )
    
    @staticmethod
    def update(record_id, **kwargs):
        """Actualizar registro de comisión."""
        record = DriverCommissionHistory.query.get(record_id)
        if not record:
            raise ValueError("Registro no encontrado")
        
        # No permitir modificar fechas al actualizar
        if 'effective_from' in kwargs:
            raise ValueError("No se puede modificar la fecha de inicio de un registro existente")
        if 'effective_until' in kwargs:
            raise ValueError("No se puede modificar la fecha de fin de un registro existente")
        
        # Solo permitir actualizar commission_percentage
        if 'commission_percentage' in kwargs:
            record.commission_percentage = kwargs['commission_percentage']
        
        db.session.commit()
        return record
