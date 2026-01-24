"""Controlador para cálculo y gestión de liquidaciones."""
from datetime import datetime
from decimal import Decimal
import json
from sqlalchemy import and_, or_
from app.models.base import db
from app.models.payroll_period import PayrollPeriod
from app.models.payroll_summary import PayrollSummary
from app.models.payroll_detail import PayrollDetail
from app.models.payroll_other_item import PayrollOtherItem
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.expense import Expense
from app.models.advance_payment import AdvancePayment
from app.controllers.payroll_period import PayrollPeriodController


class PayrollCalculationController:
    """Controlador para cálculo de liquidaciones."""
    
    @staticmethod
    def generate_summaries(period_id, driver_ids=None, is_manual=False):
        """
        Generar resúmenes de liquidación para el período.
        
        Args:
            period_id: ID del período
            driver_ids: Lista de IDs de choferes (None = todos los activos)
            is_manual: True si es generación manual, False si es automática
        
        Returns:
            Lista de resúmenes generados
        """
        period = PayrollPeriodController.get_period(period_id)
        
        # Si no se especifican choferes, obtener todos los activos
        if not driver_ids:
            drivers = Driver.query.filter_by(active=True).all()
        else:
            drivers = Driver.query.filter(Driver.id.in_(driver_ids)).all()
        
        summaries = []
        for driver in drivers:
            # Verificar que no exista un resumen aprobado
            existing_approved = PayrollSummary.query.filter_by(
                period_id=period_id,
                driver_id=driver.id,
                status='approved'
            ).first()
            
            if existing_approved:
                raise ValueError(
                    f"Ya existe un resumen aprobado para el chofer {driver.user.name} {driver.user.surname} en este período"
                )
            
            # Eliminar resumen draft/pending/error existente (regenerar)
            existing = PayrollSummary.query.filter(
                and_(
                    PayrollSummary.period_id == period_id,
                    PayrollSummary.driver_id == driver.id,
                    PayrollSummary.status.in_(['draft', 'pending_approval', 'error', 'calculation_pending'])
                )
            ).first()
            
            if existing:
                db.session.delete(existing)
                db.session.flush()
            
            # Generar nuevo resumen
            summary = PayrollCalculationController._calculate_summary(
                period, driver, is_manual
            )
            summaries.append(summary)
        
        db.session.commit()
        return summaries
    
    @staticmethod
    def _calculate_summary(period, driver, is_manual):
        """Calcular el resumen de liquidación para un chofer."""
        # Obtener el porcentaje de comisión vigente al final del período
        commission_pct = PayrollCalculationController._get_driver_commission(
            driver.id, period.end_date
        )
        
        # Obtener el mínimo garantizado vigente al final del período
        minimum_guaranteed = PayrollCalculationController._get_minimum_guaranteed(
            driver.id, period.end_date
        )
        
        # Inicializar resumen
        summary = PayrollSummary(
            period_id=period.id,
            driver_id=driver.id,
            driver_commission_percentage=commission_pct,
            driver_minimum_guaranteed=minimum_guaranteed,
            status='draft',  # Se actualizará después
            commission_from_trips=Decimal('0.00'),
            expenses_to_reimburse=Decimal('0.00'),
            expenses_to_deduct=Decimal('0.00'),
            guaranteed_minimum_applied=Decimal('0.00'),
            advances_deducted=Decimal('0.00'),
            other_items_total=Decimal('0.00'),
            total_amount=Decimal('0.00')
        )
        db.session.add(summary)
        db.session.flush()  # Para obtener el ID
        
        # Verificar si hay viajes en curso para este chofer
        has_trips_in_progress = PayrollCalculationController._check_driver_trips_in_progress(
            driver.id, period
        )
        
        # 1. Calcular comisión por viajes (validar tarifas)
        commission_result = PayrollCalculationController._calculate_trip_commission(
            summary, period, driver, commission_pct
        )
        
        if commission_result['has_error']:
            # Hay viajes sin tarifa
            summary.status = 'error'
            summary.error_message = commission_result['error_message']
            summary.commission_from_trips = Decimal('0.00')
            return summary
        
        commission_from_trips = commission_result['commission']
        
        # 2. Calcular gastos a reintegrar y a descontar
        expenses_result = PayrollCalculationController._calculate_expenses(summary, period, driver)
        expenses_to_reimburse = expenses_result[0]
        expenses_to_deduct = expenses_result[1]
        
        # 3. Calcular adelantos a descontar
        advances_deducted = PayrollCalculationController._calculate_advances(
            summary, period, driver
        )
        
        # 4. Calcular otros conceptos (ajustes, bonificaciones, cargos extra, multas sin viaje)
        other_items_total = PayrollCalculationController._calculate_other_items(
            summary, period, driver
        )
        
        # 5. Calcular mínimo garantizado si aplica
        guaranteed_minimum_applied = Decimal('0.00')
        if commission_from_trips < minimum_guaranteed:
            guaranteed_minimum_applied = minimum_guaranteed - commission_from_trips
        
        # 6. Calcular total final
        total_amount = (
            commission_from_trips +
            expenses_to_reimburse +
            guaranteed_minimum_applied +
            other_items_total -
            expenses_to_deduct -
            advances_deducted
        )
        
        # Actualizar resumen con totales
        summary.commission_from_trips = commission_from_trips
        summary.expenses_to_reimburse = expenses_to_reimburse
        summary.expenses_to_deduct = expenses_to_deduct
        summary.guaranteed_minimum_applied = guaranteed_minimum_applied
        summary.advances_deducted = advances_deducted
        summary.other_items_total = other_items_total
        summary.total_amount = total_amount
        
        # Determinar estado final
        if is_manual:
            summary.status = 'draft'
        else:
            # Generación automática
            if has_trips_in_progress:
                summary.status = 'calculation_pending'
            else:
                summary.status = 'pending_approval'
        
        return summary
    
    @staticmethod
    def _check_driver_trips_in_progress(driver_id, period):
        """Verificar si el chofer tiene viajes en curso en el período."""
        trips_in_progress = Trip.query.filter(
            and_(
                Trip.driver_id == driver_id,
                Trip.start_date >= period.start_date,
                Trip.start_date <= period.end_date,
                Trip.state_id.in_(['Pendiente', 'En curso'])
            )
        ).count()
        
        return trips_in_progress > 0
    
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
        
        # Si no hay registro, error
        raise ValueError(f"No se encontró comisión configurada para el chofer {driver_id}")
    
    @staticmethod
    def _get_minimum_guaranteed(driver_id, reference_date):
        """Obtener el mínimo garantizado del chofer vigente en una fecha."""
        from app.models.minimum_guaranteed_history import MinimumGuaranteedHistory
        
        # Buscar el mínimo garantizado vigente en la fecha de referencia
        minimum_record = MinimumGuaranteedHistory.query.filter(
            and_(
                MinimumGuaranteedHistory.driver_id == driver_id,
                MinimumGuaranteedHistory.effective_from <= reference_date,
                or_(
                    MinimumGuaranteedHistory.effective_until.is_(None),
                    MinimumGuaranteedHistory.effective_until >= reference_date
                )
            )
        ).order_by(MinimumGuaranteedHistory.effective_from.desc()).first()
        
        if minimum_record:
            return minimum_record.minimum_guaranteed
        
        # Si no hay registro, usar 0
        return Decimal('0.00')
    
    @staticmethod
    def _calculate_trip_commission(summary, period, driver, commission_pct):
        """
        Calcular comisión por viajes del período.
        Incluye SOLO viajes FINALIZADOS que iniciaron en el período.
        Valida que todos los viajes tengan tarifa.
        """
        # Obtener viajes finalizados del chofer que INICIARON en el período
        trips = Trip.query.filter(
            and_(
                Trip.driver_id == driver.id,
                Trip.start_date >= period.start_date,
                Trip.start_date <= period.end_date,
                Trip.state_id == 'Finalizado'
            )
        ).all()
        
        # Validar que todos los viajes tengan tarifa
        trips_without_rate = []
        for trip in trips:
            if trip.rate is None or trip.rate == 0:
                trips_without_rate.append(f"{trip.document_type} {trip.document_number}")
        
        if trips_without_rate:
            return {
                'has_error': True,
                'error_message': f"Los siguientes viajes no tienen tarifa cargada: {', '.join(trips_without_rate)}",
                'commission': Decimal('0.00')
            }
        
        total_base = Decimal('0.00')
        
        for trip in trips:
            trip_amount = Decimal('0.00')
            calculation_data = {}
            
            # Determinar si el cálculo es por km o por tonelada
            if trip.calculated_per_km:
                # Cálculo por kilómetro
                if trip.estimated_kms and trip.rate:
                    km = Decimal(str(trip.estimated_kms))
                    rate = Decimal(str(trip.rate))
                    trip_amount = km * rate
                    calculation_data['kilometers'] = float(trip.estimated_kms)
                    calculation_data['rate_per_km'] = float(rate)
                    calculation_data['calculation_type'] = 'per_km'
            else:
                # Cálculo por tonelada
                if trip.load_weight_on_unload and trip.rate:
                    tonnage = Decimal(str(trip.load_weight_on_unload)) / Decimal('1000')  # kg a toneladas
                    rate = Decimal(str(trip.rate))
                    trip_amount = tonnage * rate
                    calculation_data['tonnage'] = float(tonnage)
                    calculation_data['rate_per_ton'] = float(rate)
                    calculation_data['calculation_type'] = 'per_tonnage'
            
            if trip_amount > 0:
                total_base += trip_amount
                
                # Calcular la comisión de este viaje
                trip_commission = trip_amount * (commission_pct / Decimal('100'))
                
                # Agregar datos del cálculo
                calculation_data['base_amount'] = float(trip_amount)
                calculation_data['commission_percentage'] = float(commission_pct)
                calculation_data['commission_amount'] = float(trip_commission)
                
                # Crear detalle
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='trip_commission',
                    trip_id=trip.id,
                    description=f"Viaje {trip.document_type} {trip.document_number} - {trip.origin} → {trip.destination}",
                    amount=trip_commission,
                    calculation_data=json.dumps(calculation_data)
                )
                db.session.add(detail)
        
        # Retornar total de comisiones
        commission = total_base * (commission_pct / Decimal('100'))
        return {
            'has_error': False,
            'error_message': None,
            'commission': commission
        }
    
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
            
            if expense.expense_type == 'Multa':
                # Multas: siempre se descuentan
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
                # Reparaciones: depende de paid_by_admin
                if expense.paid_by_admin is False:
                    # Lo pagó el chofer, se reintegra
                    expenses_to_reimburse += amount
                    detail = PayrollDetail(
                        summary_id=summary.id,
                        detail_type='expense_reimburse',
                        expense_id=expense.id,
                        description=f"Reparación - {expense.repair_type or expense.description or ''}",
                        amount=amount
                    )
                    db.session.add(detail)
                # Si paid_by_admin es True, no se hace nada (lo pagó admin)
            
            elif expense.expense_type == 'Combustible':
                # Combustible sin vale: se reintegra
                expenses_to_reimburse += amount
                detail = PayrollDetail(
                    summary_id=summary.id,
                    detail_type='expense_reimburse',
                    expense_id=expense.id,
                    description=f"Combustible - {expense.fuel_liters}L",
                    amount=amount
                )
                db.session.add(detail)
            
            elif expense.expense_type == 'Peaje':
                # Peaje: depende de paid_by_admin
                if expense.paid_by_admin is False:
                    # Lo pagó el chofer, se reintegra
                    expenses_to_reimburse += amount
                    detail = PayrollDetail(
                        summary_id=summary.id,
                        detail_type='expense_reimburse',
                        expense_id=expense.id,
                        description=f"Peaje - {expense.toll_port_fee_name or expense.description or ''}",
                        amount=amount
                    )
                    db.session.add(detail)
                # Si paid_by_admin es True, no se hace nada (lo pagó admin)
            
            elif expense.expense_type == 'Viáticos':
                # Viáticos: siempre se reintegran (gastos extraordinarios)
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
        """Calcular adelantos a descontar (administrador + cliente)."""
        # 1. Adelantos dados por el administrador
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
        
        # 2. Adelantos dados por el cliente (asociados a viajes del período)
        trips_with_client_advance = Trip.query.filter(
            and_(
                Trip.driver_id == driver.id,
                Trip.start_date >= period.start_date,
                Trip.start_date <= period.end_date,
                Trip.client_advance_payment.isnot(None),
                Trip.client_advance_payment > 0
            )
        ).all()
        
        for trip in trips_with_client_advance:
            amount = Decimal(str(trip.client_advance_payment))
            total_advances += amount
            
            detail = PayrollDetail(
                summary_id=summary.id,
                detail_type='client_advance',
                trip_id=trip.id,
                description=f"Adelanto del cliente - Viaje {trip.document_type} {trip.document_number}",
                amount=amount
            )
            db.session.add(detail)
        
        return total_advances
    
    @staticmethod
    def _calculate_other_items(summary, period, driver):
        """Calcular otros conceptos (ajustes, bonificaciones, cargos extra, multas sin viaje)."""
        other_items = PayrollOtherItem.query.filter(
            and_(
                PayrollOtherItem.driver_id == driver.id,
                PayrollOtherItem.period_id == period.id
            )
        ).all()
        
        total_other_items = Decimal('0.00')
        
        for item in other_items:
            amount = Decimal(str(item.amount))
            total_other_items += amount
            
            # Determinar el tipo de detalle
            if item.item_type == 'adjustment':
                detail_type = 'other_item_adjustment'
            elif item.item_type == 'bonus':
                detail_type = 'other_item_bonus'
            elif item.item_type == 'extra_charge':
                detail_type = 'other_item_charge'
            elif item.item_type == 'fine_without_trip':
                detail_type = 'other_item_fine'
            else:
                detail_type = 'other_item'
            
            detail = PayrollDetail(
                summary_id=summary.id,
                detail_type=detail_type,
                description=f"{item.item_type.replace('_', ' ').title()} - {item.description}",
                amount=amount
            )
            db.session.add(detail)
        
        return total_other_items
    
    @staticmethod
    def recalculate_summary(summary_id):
        """
        Recalcular un resumen existente.
        El resumen actual pasa a 'draft' y se genera uno nuevo 'pending_approval'.
        """
        # Obtener el resumen actual
        current_summary = PayrollSummary.query.get(summary_id)
        if not current_summary:
            raise ValueError("Resumen no encontrado")
        
        # Solo se puede recalcular si está en pending_approval o error
        if current_summary.status not in ['pending_approval', 'error']:
            raise ValueError(f"Solo se pueden recalcular resúmenes en estado 'pending_approval' o 'error'. Estado actual: {current_summary.status}")
        
        # Cambiar el estado del resumen actual a draft
        current_summary.status = 'draft'
        current_summary.notes = (current_summary.notes or '') + f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Reemplazado por recálculo"
        
        # Obtener período y chofer
        period = PayrollPeriod.query.get(current_summary.period_id)
        driver = Driver.query.get(current_summary.driver_id)
        
        # Generar nuevo resumen
        new_summary = PayrollCalculationController._calculate_summary(
            period, driver, is_manual=False
        )
        
        db.session.commit()
        return new_summary
    
    @staticmethod
    def update_calculation_pending_summaries():
        """
        Actualizar resúmenes en estado 'calculation_pending'.
        Se ejecuta cuando se finaliza un viaje para verificar si ahora se puede calcular.
        """
        pending_summaries = PayrollSummary.query.filter_by(status='calculation_pending').all()
        
        for summary in pending_summaries:
            # Verificar si aún hay viajes en curso
            period = PayrollPeriod.query.get(summary.period_id)
            has_trips_in_progress = PayrollCalculationController._check_driver_trips_in_progress(
                summary.driver_id, period
            )
            
            if not has_trips_in_progress:
                # Ya no hay viajes en curso, recalcular
                driver = Driver.query.get(summary.driver_id)
                
                # Eliminar el resumen pending
                db.session.delete(summary)
                db.session.flush()
                
                # Generar nuevo resumen
                new_summary = PayrollCalculationController._calculate_summary(
                    period, driver, is_manual=False
                )
        
        db.session.commit()
    
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
        
        if summary.status != 'pending_approval':
            raise ValueError(f"Solo se pueden aprobar resúmenes en estado 'pending_approval'. Estado actual: {summary.status}")
        
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
