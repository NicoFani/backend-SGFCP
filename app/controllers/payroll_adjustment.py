"""Controlador para ajustes retroactivos de liquidación."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_
from app.models.base import db
from app.models.payroll_adjustment import PayrollAdjustment
from app.models.payroll_period import PayrollPeriod
from app.models.driver import Driver
from app.controllers.payroll_period import PayrollPeriodController


class PayrollAdjustmentController:
    """Controlador para ajustes retroactivos."""
    
    @staticmethod
    def auto_create_trip_adjustment(trip):
        """
        Crear ajuste automático cuando se finaliza un viaje que pertenece a un período cerrado.
        
        Args:
            trip: El viaje que se acaba de finalizar
            
        Returns:
            PayrollAdjustment o None si no se creó ajuste
        """
        from app.models.trip import Trip
        from app.controllers.payroll_settings import PayrollSettingsController
        
        # Verificar que el viaje esté finalizado
        if trip.state_id != 'Finalizado':
            return None
        
        # Buscar el período al que pertenece (por start_date)
        if not trip.start_date:
            return None
        
        period = PayrollPeriod.query.filter(
            and_(
                PayrollPeriod.start_date <= trip.start_date,
                PayrollPeriod.end_date >= trip.start_date,
                PayrollPeriod.status.in_(['closed', 'with_adjustments'])
            )
        ).first()
        
        # Si no hay período cerrado, no se crea ajuste
        if not period:
            return None
        
        # Calcular el monto del ajuste (comisión del viaje)
        # Usar la comisión por defecto del sistema
        settings = PayrollSettingsController.get_current_settings()
        commission_pct = Decimal(str(settings.default_commission_percentage)) / Decimal('100')
        
        trip_amount = Decimal('0.00')
        
        # Calcular por tonelada
        if trip.load_weight_on_unload and trip.rate_per_ton:
            tonnage = Decimal(str(trip.load_weight_on_unload)) / Decimal('1000')
            rate = Decimal(str(trip.rate_per_ton))
            trip_amount += tonnage * rate
        
        # Calcular por kilómetro
        if trip.estimated_kms and trip.rate_per_ton:  # Nota: Trip no tiene rate_per_km ni kilometers
            km = Decimal(str(trip.estimated_kms))
            # Por ahora, solo calculamos por tonelada
            # rate_km = Decimal(str(trip.rate_per_km))
            # trip_amount += km * rate_km
        
        # Aplicar comisión
        adjustment_amount = trip_amount * commission_pct
        
        if adjustment_amount <= 0:
            return None
        
        # Crear ajustes para CADA chofer del viaje (relación many-to-many)
        adjustments = []
        
        for driver in trip.drivers:
            adjustment = PayrollAdjustment(
                origin_period_id=period.id,
                driver_id=driver.id,
                trip_id=trip.id,
                amount=adjustment_amount,
                description=f"Viaje finalizado post-cierre: {trip.document_type} {trip.document_number}",
                adjustment_type='trip_correction',
                created_by=1,  # Sistema
                is_applied='pending'
            )
            
            db.session.add(adjustment)
            adjustments.append(adjustment)
        
        # Marcar período como "with_adjustments"
        if period.status == 'closed':
            period.status = 'with_adjustments'
        
        db.session.commit()
        
        return adjustments if adjustments else None
    
    @staticmethod
    def create_adjustment(origin_period_id, driver_id, amount, description, 
                         adjustment_type, created_by, trip_id=None, expense_id=None):
        """Crear un ajuste retroactivo manual."""
        # Validar período origen
        origin_period = PayrollPeriodController.get_period(origin_period_id)
        
        if origin_period.status == 'open':
            raise ValueError(
                "No se puede crear un ajuste para un período abierto. "
                "Modifique los datos directamente."
            )
        
        # Validar chofer
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError("Chofer no encontrado")
        
        # Validar monto
        amount_decimal = Decimal(str(amount))
        
        # Crear ajuste
        adjustment = PayrollAdjustment(
            origin_period_id=origin_period_id,
            driver_id=driver_id,
            trip_id=trip_id,
            expense_id=expense_id,
            amount=amount_decimal,
            description=description,
            adjustment_type=adjustment_type,
            created_by=created_by,
            is_applied='pending'
        )
        
        db.session.add(adjustment)
        db.session.commit()
        
        return adjustment
    
    @staticmethod
    def create_adjustment_from_expense(expense, origin_period_id, created_by):
        """Crear ajuste automático cuando se carga un gasto a período cerrado."""
        from app.models.expense import Expense
        
        expense_obj = Expense.query.get(expense.id)
        if not expense_obj:
            raise ValueError("Gasto no encontrado")
        
        # Determinar el monto del ajuste según el tipo de gasto
        amount = Decimal(str(expense_obj.amount))
        
        # Clasificar según reglas de negocio
        if expense_obj.expense_type == 'multa':
            # Las multas se descuentan (ajuste negativo)
            amount = -amount
            description = f"Multa cargada post-cierre: {expense_obj.description or ''}"
        
        elif expense_obj.expense_type == 'reparacion':
            if not expense_obj.paid_by_administration:
                # Reparación pagada por chofer: se reintegra (ajuste positivo)
                description = f"Reparación cargada post-cierre: {expense_obj.description or ''}"
            else:
                # No genera ajuste
                return None
        
        elif expense_obj.expense_type == 'combustible':
            if not expense_obj.has_fuel_voucher:
                # Combustible sin vale: se reintegra (ajuste positivo)
                description = f"Combustible cargado post-cierre: {expense_obj.liters}L"
            else:
                # No genera ajuste
                return None
        
        elif expense_obj.expense_type == 'peaje':
            if not expense_obj.paid_by_administration:
                # Peaje pagado por chofer: se reintegra (ajuste positivo)
                description = f"Peaje cargado post-cierre: {expense_obj.description or ''}"
            else:
                # No genera ajuste
                return None
        
        elif expense_obj.expense_type == 'gasto_extraordinario':
            # Se reintegra (ajuste positivo)
            description = f"Gasto extraordinario post-cierre: {expense_obj.description or ''}"
        
        else:
            # Tipo no reconocido, no generar ajuste
            return None
        
        # Crear el ajuste
        adjustment = PayrollAdjustmentController.create_adjustment(
            origin_period_id=origin_period_id,
            driver_id=expense_obj.driver_id,
            amount=amount,
            description=description,
            adjustment_type='expense_post_close',
            created_by=created_by,
            expense_id=expense.id
        )
        
        return adjustment
    
    @staticmethod
    def get_adjustment(adjustment_id):
        """Obtener un ajuste por ID."""
        adjustment = PayrollAdjustment.query.get(adjustment_id)
        if not adjustment:
            raise ValueError("Ajuste no encontrado")
        return adjustment
    
    @staticmethod
    def update_adjustment(adjustment_id, amount=None, description=None):
        """Actualizar un ajuste retroactivo."""
        adjustment = PayrollAdjustmentController.get_adjustment(adjustment_id)
        
        if adjustment.is_applied == 'applied':
            raise ValueError("No se puede modificar un ajuste ya aplicado")
        
        if amount is not None:
            adjustment.amount = Decimal(str(amount))
        
        if description is not None:
            adjustment.description = description
        
        db.session.commit()
        return adjustment
    
    @staticmethod
    def delete_adjustment(adjustment_id):
        """Eliminar un ajuste retroactivo."""
        adjustment = PayrollAdjustmentController.get_adjustment(adjustment_id)
        
        if adjustment.is_applied == 'applied':
            raise ValueError("No se puede eliminar un ajuste ya aplicado")
        
        db.session.delete(adjustment)
        db.session.commit()
    
    @staticmethod
    def get_all_adjustments(origin_period_id=None, driver_id=None, 
                           is_applied=None, page=1, per_page=20):
        """Obtener ajustes con filtros."""
        query = PayrollAdjustment.query
        
        if origin_period_id:
            query = query.filter_by(origin_period_id=origin_period_id)
        if driver_id:
            query = query.filter_by(driver_id=driver_id)
        if is_applied:
            query = query.filter_by(is_applied=is_applied)
        
        query = query.order_by(PayrollAdjustment.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_pending_adjustments_for_driver(driver_id):
        """Obtener ajustes pendientes de un chofer."""
        adjustments = PayrollAdjustment.query.filter(
            and_(
                PayrollAdjustment.driver_id == driver_id,
                PayrollAdjustment.is_applied == 'pending'
            )
        ).all()
        
        return adjustments
