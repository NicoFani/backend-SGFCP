"""Controlador para gestión de períodos de liquidación."""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from app.models.base import db
from app.models.payroll_period import PayrollPeriod
from app.models.trip import Trip


class PayrollPeriodController:
    """Controlador para períodos de liquidación."""
    
    @staticmethod
    def create_period(year, month, start_date=None, end_date=None):
        """Crear un nuevo período de liquidación."""
        # Verificar que no exista ya un período para ese mes/año
        existing = PayrollPeriod.query.filter_by(year=year, month=month).first()
        if existing:
            raise ValueError(f"Ya existe un período para {year}-{month:02d}")
        
        # Si no se proporcionan fechas, calcular automáticamente
        if not start_date:
            start_date = date(year, month, 1)
        if not end_date:
            # Último día del mes
            next_month = start_date + relativedelta(months=1)
            end_date = next_month - relativedelta(days=1)
        
        period = PayrollPeriod(
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            status='open',
            has_trips_in_progress=False
        )
        
        db.session.add(period)
        db.session.commit()
        
        return period
    
    @staticmethod
    def get_period(period_id):
        """Obtener un período por ID."""
        period = PayrollPeriod.query.get(period_id)
        if not period:
            raise ValueError("Período no encontrado")
        return period
    
    @staticmethod
    def get_all_periods(page=1, per_page=20, status=None):
        """Obtener todos los períodos con paginación."""
        query = PayrollPeriod.query
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_current_period():
        """Obtener el período actual o crear uno nuevo."""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        period = PayrollPeriod.query.filter_by(
            year=current_year,
            month=current_month
        ).first()
        
        if not period:
            period = PayrollPeriodController.create_period(current_year, current_month)
        
        return period
    
    @staticmethod
    def check_trips_in_progress(period_id):
        """Verificar si hay viajes en curso en el período."""
        period = PayrollPeriodController.get_period(period_id)
        
        # Buscar viajes que iniciaron en el período pero no han finalizado
        trips_in_progress = Trip.query.filter(
            and_(
                Trip.start_date >= period.start_date,
                Trip.start_date <= period.end_date,
                Trip.state_id.in_(['Pendiente', 'En curso'])
            )
        ).count()
        
        # Actualizar el estado del período
        period.has_trips_in_progress = (trips_in_progress > 0)
        db.session.commit()
        
        return trips_in_progress > 0
    
    @staticmethod
    def close_period(period_id, force=False):
        """Cerrar un período de liquidación."""
        period = PayrollPeriodController.get_period(period_id)
        
        if period.status == 'closed':
            raise ValueError("El período ya está cerrado")
        
        # Verificar viajes en curso
        if not force:
            has_trips = PayrollPeriodController.check_trips_in_progress(period_id)
            if has_trips:
                raise ValueError(
                    "No se puede cerrar el período mientras haya viajes en curso. "
                    "Use force=True para forzar el cierre."
                )
        
        period.status = 'closed'
        period.actual_close_date = datetime.utcnow()
        db.session.commit()
        
        return period
    
    @staticmethod
    def reopen_period(period_id):
        """Reabrir un período para realizar ajustes."""
        period = PayrollPeriodController.get_period(period_id)
        
        if period.status == 'open':
            raise ValueError("El período ya está abierto")
        
        period.status = 'with_adjustments'
        db.session.commit()
        
        return period
    
    @staticmethod
    def get_period_by_date(reference_date):
        """Obtener el período que contiene una fecha específica."""
        period = PayrollPeriod.query.filter(
            and_(
                PayrollPeriod.start_date <= reference_date,
                PayrollPeriod.end_date >= reference_date
            )
        ).first()
        
        if not period:
            # Crear el período si no existe
            year = reference_date.year
            month = reference_date.month
            period = PayrollPeriodController.create_period(year, month)
        
        return period
    
    @staticmethod
    def get_next_open_period():
        """Obtener el próximo período abierto para aplicar ajustes."""
        # Buscar el período abierto más reciente
        period = PayrollPeriod.query.filter_by(status='open').order_by(
            PayrollPeriod.year.desc(),
            PayrollPeriod.month.desc()
        ).first()
        
        if not period:
            # Si no hay períodos abiertos, obtener o crear el actual
            period = PayrollPeriodController.get_current_period()
        
        return period
