"""Controlador para gestión de mínimo garantizado por chofer."""
from datetime import datetime
from app.models.base import db
from app.models.minimum_guaranteed_history import MinimumGuaranteedHistory
from sqlalchemy import and_, or_


class MinimumGuaranteedController:
    """Controlador para mínimo garantizado."""
    
    @staticmethod
    def create(driver_id, minimum_guaranteed, effective_from):
        """
        Crear nuevo registro de mínimo garantizado.
        Cierra el registro anterior si existe.
        """
        # Cerrar el registro anterior vigente
        current = MinimumGuaranteedHistory.query.filter(
            and_(
                MinimumGuaranteedHistory.driver_id == driver_id,
                MinimumGuaranteedHistory.effective_until.is_(None)
            )
        ).first()
        
        if current:
            current.effective_until = effective_from
        
        # Crear nuevo registro
        new_record = MinimumGuaranteedHistory(
            driver_id=driver_id,
            minimum_guaranteed=minimum_guaranteed,
            effective_from=effective_from,
            effective_until=None
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return new_record
    
    @staticmethod
    def get_by_id(record_id):
        """Obtener registro por ID."""
        return MinimumGuaranteedHistory.query.get(record_id)
    
    @staticmethod
    def get_all(driver_id=None):
        """Obtener todos los registros, opcionalmente filtrados por chofer."""
        query = MinimumGuaranteedHistory.query
        
        if driver_id:
            query = query.filter_by(driver_id=driver_id)
        
        return query.order_by(MinimumGuaranteedHistory.effective_from.desc()).all()
    
    @staticmethod
    def get_current(driver_id):
        """Obtener el mínimo garantizado vigente para un chofer."""
        return MinimumGuaranteedHistory.query.filter(
            and_(
                MinimumGuaranteedHistory.driver_id == driver_id,
                MinimumGuaranteedHistory.effective_until.is_(None)
            )
        ).first()
    
    @staticmethod
    def get_at_date(driver_id, reference_date):
        """Obtener el mínimo garantizado vigente en una fecha específica."""
        return MinimumGuaranteedHistory.query.filter(
            and_(
                MinimumGuaranteedHistory.driver_id == driver_id,
                MinimumGuaranteedHistory.effective_from <= reference_date,
                or_(
                    MinimumGuaranteedHistory.effective_until.is_(None),
                    MinimumGuaranteedHistory.effective_until >= reference_date
                )
            )
        ).order_by(MinimumGuaranteedHistory.effective_from.desc()).first()
    
    @staticmethod
    def update(record_id, **kwargs):
        """Actualizar registro."""
        record = MinimumGuaranteedHistory.query.get(record_id)
        if not record:
            raise ValueError("Registro no encontrado")
        
        # No permitir modificar fechas al actualizar
        if 'effective_from' in kwargs:
            raise ValueError("No se puede modificar la fecha de inicio de un registro existente")
        if 'effective_until' in kwargs:
            raise ValueError("No se puede modificar la fecha de fin de un registro existente")
        
        # Solo permitir actualizar minimum_guaranteed
        if 'minimum_guaranteed' in kwargs:
            record.minimum_guaranteed = kwargs['minimum_guaranteed']
        
        db.session.commit()
        return record
    
    @staticmethod
    def delete(record_id):
        """Eliminar registro."""
        record = MinimumGuaranteedHistory.query.get(record_id)
        if not record:
            raise ValueError("Registro no encontrado")
        
        db.session.delete(record)
        db.session.commit()
