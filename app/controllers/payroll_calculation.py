"""Controlador para cálculo y gestión de liquidaciones."""
from datetime import datetime
from decimal import Decimal
import json
from sqlalchemy import and_, or_
from app.models.base import db
from app.models.payroll_period import PayrollPeriod
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_detail import PayrollDetail
from app.models.payroll_adjustment import PayrollAdjustment
from app.models.payroll_settings import PayrollSettings
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.expense import Expense
from app.models.advance_payment import AdvancePayment
from app.controllers.payroll_period import PayrollPeriodController
from app.controllers.payroll_settings import PayrollSettingsController


class PayrollCalculationController:
    """Controlador para cálculo de liquidaciones."""
    
    @staticmethod
    def generate_summaries(period_id, driver_ids=None, calculation_type='both'):
        """
        Generar resúmenes de liquidación para el período.
        
        IMPORTANTE: La generación se realiza siempre, incluso si hay viajes en curso.
        Los viajes iniciados en el período pero no finalizados serán incluidos 
        cuando se finalicen (se aplican como ajustes retroactivos automáticos).
        """
        period = PayrollPeriodController.get_period(period_id)
        
        # Verificar y marcar si hay viajes en curso (informativo, no bloquea)
        PayrollPeriodController.check_trips_in_progress(period_id)
        
        # Si no se especifican choferes, obtener todos los activos
        if not driver_ids:
            drivers = Driver.query.filter_by(active=True).all()
            driver_ids = [d.id for d in drivers]
        else:
            drivers = Driver.query.filter(Driver.id.in_(driver_ids)).all()
        
        summaries = []
        for driver in drivers:
            # Eliminar resumen existente si existe (regenerar)
            existing = PayrollSummary.query.filter_by(
                period_id=period_id,
                driver_id=driver.id,
                calculation_type=calculation_type
            ).first()
            
            if existing and existing.status == 'approved':
                raise ValueError(
                    f"El resumen para el chofer {driver.full_name} ya está aprobado. "
                    "No se puede regenerar."
                )
            
            if existing:
                db.session.delete(existing)
            
            # Generar nuevo resumen
            summary = PayrollCalculationController._calculate_summary(
                period, driver, calculation_type
            )
            summaries.append(summary)
        
        db.session.commit()
        return summaries
    
    @staticmethod
    def _calculate_summary(period, driver, calculation_type):
        """Calcular el resumen de liquidación para un chofer."""
        # Obtener el porcentaje de comisión vigente al final del período
        commission_pct = PayrollCalculationController._get_driver_commission(
            driver.id, period.end_date
        )
        
        # Inicializar resumen
        summary = PayrollSummary(
            period_id=period.id,
            driver_id=driver.id,
            calculation_type=calculation_type,
            driver_commission_percentage=commission_pct,
            status='draft',
            # Inicializar todos los campos para evitar NULL constraint
            commission_from_trips=Decimal('0.00'),
            expenses_to_reimburse=Decimal('0.00'),
            expenses_to_deduct=Decimal('0.00'),
            guaranteed_minimum_applied=Decimal('0.00'),
            advances_deducted=Decimal('0.00'),
            adjustments_applied=Decimal('0.00'),
            total_amount=Decimal('0.00')
        )
        db.session.add(summary)
        db.session.flush()  # Para obtener el ID
        
        # 1. Calcular comisión por viajes
        commission_from_trips = PayrollCalculationController._calculate_trip_commission(
            summary, period, driver, calculation_type, commission_pct
        )
        if commission_from_trips is None:
            commission_from_trips = Decimal('0.00')
        
        # 2. Calcular gastos a reintegrar y a descontar
        expenses_result = PayrollCalculationController._calculate_expenses(summary, period, driver)
        expenses_to_reimburse = expenses_result[0] if expenses_result else Decimal('0.00')
        expenses_to_deduct = expenses_result[1] if expenses_result and len(expenses_result) > 1 else Decimal('0.00')
        
        # 3. Calcular adelantos a descontar
        advances_deducted = PayrollCalculationController._calculate_advances(
            summary, period, driver
        )
        if advances_deducted is None:
            advances_deducted = Decimal('0.00')
        
        # 4. Aplicar ajustes retroactivos pendientes
        adjustments_applied = PayrollCalculationController._apply_adjustments(
            summary, period, driver
        )
        if adjustments_applied is None:
            adjustments_applied = Decimal('0.00')
        
        # 5. Calcular mínimo garantizado si aplica
        settings = PayrollSettingsController.get_current_settings()
        guaranteed_minimum_applied = Decimal('0.00')
        
        # Convertir guaranteed_minimum a Decimal si no lo es
        guaranteed_minimum = Decimal(str(settings.guaranteed_minimum))
        
        if commission_from_trips < guaranteed_minimum:
            guaranteed_minimum_applied = guaranteed_minimum - commission_from_trips
        
        # 6. Calcular total final - simplificado sin conversiones redundantes
        total_amount = (
            commission_from_trips +
            expenses_to_reimburse +
            guaranteed_minimum_applied +
            adjustments_applied -
            expenses_to_deduct -
            advances_deducted
        )
        
        # Asegurar que total_amount no sea None
        if total_amount is None:
            total_amount = Decimal('0.00')
        
        # Actualizar resumen con totales
        summary.commission_from_trips = commission_from_trips
        summary.expenses_to_reimburse = expenses_to_reimburse
        summary.expenses_to_deduct = expenses_to_deduct
        summary.guaranteed_minimum_applied = guaranteed_minimum_applied
        summary.advances_deducted = advances_deducted
        summary.adjustments_applied = adjustments_applied
        summary.total_amount = total_amount
        
        # NO hacer commit aquí - se hará en generate_summaries después de procesar todos los drivers
        
        return summary
    
    @staticmethod
    def _get_driver_commission(driver_id, reference_date):
        """Obtener el porcentaje de comisión del chofer vigente en una fecha."""
        from app.models.driver_commission_history import DriverCommissionHistory
        
        # Buscar el porcentaje vigente en la fecha de referencia
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
        
        # Si no hay registro, usar el porcentaje por defecto
        settings = PayrollSettingsController.get_current_settings()
        return settings.default_commission_percentage
    
    @staticmethod
    def _calculate_trip_commission(summary, period, driver, calculation_type, commission_pct):
        """
        Calcular comisión por viajes del período.
        
        Incluye SOLO viajes FINALIZADOS que iniciaron en el período.
        Los viajes iniciados pero NO finalizados se aplicarán como ajuste retroactivo
        cuando se finalicen.
        """
        # Obtener viajes finalizados del chofer que INICIARON en el período
        # Usar join porque la relación es many-to-many
        trips = Trip.query.join(Trip.drivers).filter(
            and_(
                Driver.id == driver.id,
                Trip.start_date >= period.start_date,
                Trip.start_date <= period.end_date,
                Trip.state_id == 'Finalizado'
            )
        ).all()
        
        total_base = Decimal('0.00')
        
        for trip in trips:
            trip_amount = Decimal('0.00')
            calculation_data = {}
            
            # Cálculo por tonelada
            if calculation_type in ['by_tonnage', 'both']:
                if trip.load_weight_on_unload and trip.rate_per_ton:
                    tonnage = Decimal(str(trip.load_weight_on_unload)) / Decimal('1000')  # kg a toneladas
                    rate = Decimal(str(trip.rate_per_ton))
                    trip_amount += tonnage * rate
                    calculation_data['tonnage'] = float(tonnage)
                    calculation_data['rate_per_ton'] = float(rate)
            
            # Cálculo por kilómetro
            if calculation_type in ['by_km', 'both']:
                if trip.estimated_kms and trip.km_rate:
                    km = Decimal(str(trip.estimated_kms))
                    rate_km = Decimal(str(trip.km_rate))
                    trip_amount += km * rate_km
                    calculation_data['kilometers'] = float(trip.estimated_kms)
                    calculation_data['km_rate'] = float(rate_km)
            
            if trip_amount > 0:
                total_base += trip_amount
                
                # Calcular la comisión de este viaje
                trip_commission = trip_amount * (commission_pct / Decimal('100'))
                
                # Agregar datos del cálculo
                calculation_data['base_amount'] = float(trip_amount)
                calculation_data['commission_percentage'] = float(commission_pct)
                calculation_data['commission_amount'] = float(trip_commission)
                
                # Crear detalle con la COMISIÓN calculada, no el monto base
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='trip_commission',
                    trip_id=trip.id,
                    description=f"Viaje {trip.document_type} {trip.document_number} - {trip.origin} a {trip.destination} ({float(trip_amount):.2f} × {float(commission_pct)}%)",
                    amount=trip_commission,
                    calculation_data=json.dumps(calculation_data)
                )
                db.session.add(detail)
        
        # Retornar total de comisiones
        commission = total_base * (commission_pct / Decimal('100'))
        return commission
    
    @staticmethod
    def _calculate_expenses(summary, period, driver):
        """Calcular gastos a reintegrar y a descontar."""
        # Obtener gastos del chofer en el período
        expenses = Expense.query.filter(
            and_(
                Expense.driver_id == driver.id,
                Expense.date >= period.start_date,
                Expense.date <= period.end_date
            )
        ).all()
        
        expenses_to_reimburse = Decimal('0.00')
        expenses_to_deduct = Decimal('0.00')
        
        for expense in expenses:
            amount = Decimal(str(expense.amount))
            
            # Clasificar según tipo de gasto (valores del enum: 'Viáticos', 'Multa', 'Reparaciones', 'Combustible', 'Peaje')
            if expense.expense_type == 'Multa':
                # Multas: se descuentan totalmente
                expenses_to_deduct += amount
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='expense_deduct',
                    expense_id=expense.id,
                    description=f"Multa - {expense.description or 'Sin descripción'}",
                    amount=amount
                )
                db.session.add(detail)
            
            elif expense.expense_type == 'Reparaciones':
                # Reparaciones: se reintegran (asumimos que las pagó el chofer)
                expenses_to_reimburse += amount
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='expense_reimburse',
                    expense_id=expense.id,
                    description=f"Reparación - {expense.description or ''}",
                    amount=amount
                )
                db.session.add(detail)
            
            elif expense.expense_type == 'Combustible':
                # Combustible: se reintegra (asumimos que las pagó el chofer)
                expenses_to_reimburse += amount
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='expense_reimburse',
                    expense_id=expense.id,
                    description=f"Combustible - {expense.description or ''}",
                    amount=amount
                )
                db.session.add(detail)
            
            elif expense.expense_type == 'Peaje':
                # Peaje: se reintegra si lo pagó el chofer
                if expense.toll_paid_by == 'Chofer':
                    expenses_to_reimburse += amount
                    detail = PayrollDetail(
                        summary_id=summary.id,
                        detail_type='expense_reimburse',
                        expense_id=expense.id,
                        description=f"Peaje - {expense.description or ''}",
                        amount=amount
                    )
                    db.session.add(detail)
            
            elif expense.expense_type == 'Viáticos':
                # Viáticos: se reintegran totalmente
                expenses_to_reimburse += amount
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='expense_reimburse',
                    expense_id=expense.id,
                    description=f"Viáticos - {expense.description or ''}",
                    amount=amount
                )
                db.session.add(detail)
        
        return expenses_to_reimburse, expenses_to_deduct
    
    @staticmethod
    def _calculate_advances(summary, period, driver):
        """Calcular adelantos a descontar."""
        # Obtener adelantos del período
        advances = AdvancePayment.query.filter(
            and_(
                AdvancePayment.driver_id == driver.id,
                AdvancePayment.date >= period.start_date,
                AdvancePayment.date <= period.end_date
            )
        ).all()
        
        total_advances = Decimal('0.00')
        
        for advance in advances:
            amount = Decimal(str(advance.amount))
            total_advances += amount
            
            detail = PayrollDetail(
                summary_id=summary.id,
                detail_type='advance',
                advance_id=advance.id,
                description=f"Adelanto del {advance.date.strftime('%d/%m/%Y')}",
                amount=amount
            )
            db.session.add(detail)
        
        return total_advances
    
    @staticmethod
    def _apply_adjustments(summary, period, driver):
        """Aplicar ajustes retroactivos pendientes."""
        # Obtener ajustes pendientes para este chofer
        adjustments = PayrollAdjustment.query.filter(
            and_(
                PayrollAdjustment.driver_id == driver.id,
                PayrollAdjustment.is_applied == 'pending'
            )
        ).all()
        
        total_adjustments = Decimal('0.00')
        
        for adjustment in adjustments:
            amount = Decimal(str(adjustment.amount))
            total_adjustments += amount
            
            detail = PayrollDetail(
                summary_id=summary.id,
                detail_type='adjustment',
                adjustment_id=adjustment.id,
                description=f"Ajuste período {adjustment.origin_period_id}: {adjustment.description}",
                amount=amount
            )
            db.session.add(detail)
            
            # Marcar ajuste como aplicado
            adjustment.is_applied = 'applied'
            adjustment.applied_in_period_id = period.id
        
        return total_adjustments
    
    @staticmethod
    def get_summary(summary_id):
        """Obtener un resumen de liquidación."""
        summary = PayrollSummary.query.get(summary_id)
        if not summary:
            raise ValueError("Resumen no encontrado")
        return summary
    
    @staticmethod
    def get_summary_details(summary_id):
        """Obtener los detalles de un resumen."""
        summary = PayrollCalculationController.get_summary(summary_id)
        details = PayrollDetail.query.filter_by(summary_id=summary_id).all()
        return summary, details
    
    @staticmethod
    def approve_summary(summary_id, notes=None):
        """Aprobar un resumen de liquidación."""
        summary = PayrollCalculationController.get_summary(summary_id)
        
        if summary.status == 'approved':
            raise ValueError("El resumen ya está aprobado")
        
        summary.status = 'approved'
        if notes:
            summary.notes = notes
        
        db.session.commit()
        return summary
    
    @staticmethod
    def get_all_summaries(period_id=None, driver_id=None, status=None, page=1, per_page=20):
        """Obtener resúmenes con filtros."""
        query = PayrollSummary.query
        
        if period_id:
            query = query.filter_by(period_id=period_id)
        if driver_id:
            query = query.filter_by(driver_id=driver_id)
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(PayrollSummary.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
