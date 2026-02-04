"""Controlador para gestión de otros conceptos de liquidación."""
from datetime import datetime
from decimal import Decimal
from app.models.base import db
from app.models.payroll_other_item import PayrollOtherItem


class PayrollOtherItemController:
    """Controlador para otros conceptos (ajustes, bonificaciones, cargos, multas)."""

    @staticmethod
    def _normalize_amount(amount, item_type):
        """Aplicar reglas de negocio sobre el signo del importe."""
        if amount is None:
            return amount

        value = Decimal(str(amount))
        if item_type == 'bonus':
            return abs(value)
        if item_type in ['extra_charge', 'fine_without_trip']:
            return -abs(value)
        # adjustment: puede sumar o restar
        return value
    
    @staticmethod
    def create(driver_id, period_id, item_type, description, amount, date, 
               created_by, reference=None, receipt_url=None):
        """Crear nuevo concepto."""
        normalized_amount = PayrollOtherItemController._normalize_amount(amount, item_type)
        item = PayrollOtherItem(
            driver_id=driver_id,
            period_id=period_id,
            item_type=item_type,
            description=description,
            amount=normalized_amount,
            date=date,
            reference=reference,
            receipt_url=receipt_url,
            created_by=created_by
        )
        
        db.session.add(item)
        db.session.commit()
        
        return item
    
    @staticmethod
    def get_by_id(item_id):
        """Obtener concepto por ID."""
        return PayrollOtherItem.query.get(item_id)
    
    @staticmethod
    def get_all(driver_id=None, period_id=None, item_type=None, page=1, per_page=20):
        """Obtener todos los conceptos con filtros opcionales."""
        query = PayrollOtherItem.query
        
        if driver_id:
            query = query.filter_by(driver_id=driver_id)
        if period_id:
            query = query.filter_by(period_id=period_id)
        if item_type:
            query = query.filter_by(item_type=item_type)
        
        query = query.order_by(PayrollOtherItem.date.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_period_and_driver(period_id, driver_id):
        """Obtener todos los conceptos de un chofer en un período."""
        return PayrollOtherItem.query.filter_by(
            period_id=period_id,
            driver_id=driver_id
        ).order_by(PayrollOtherItem.date.desc()).all()
    
    @staticmethod
    def update(item_id, **kwargs):
        """Actualizar concepto."""
        item = PayrollOtherItem.query.get(item_id)
        if not item:
            raise ValueError("Concepto no encontrado")
        
        # Actualizar campos permitidos
        allowed_fields = ['description', 'amount', 'date', 'reference', 'receipt_url', 'item_type']
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(item, key):
                setattr(item, key, value)

        # Re-normalizar monto si corresponde
        if 'amount' in kwargs or 'item_type' in kwargs:
            item.amount = PayrollOtherItemController._normalize_amount(item.amount, item.item_type)
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return item
    
    @staticmethod
    def delete(item_id):
        """Eliminar concepto."""
        item = PayrollOtherItem.query.get(item_id)
        if not item:
            raise ValueError("Concepto no encontrado")
        
        db.session.delete(item)
        db.session.commit()
    
    @staticmethod
    def get_summary_by_type(period_id, driver_id):
        """Obtener resumen de conceptos por tipo para un chofer en un período."""
        items = PayrollOtherItem.query.filter_by(
            period_id=period_id,
            driver_id=driver_id
        ).all()
        
        summary = {
            'adjustment': 0,
            'bonus': 0,
            'extra_charge': 0,
            'fine_without_trip': 0,
            'total': 0
        }
        
        for item in items:
            if item.item_type in summary:
                summary[item.item_type] += float(item.amount)
            summary['total'] += float(item.amount)
        
        return summary
