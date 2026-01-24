"""Tareas programadas para la aplicación SGFCP."""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.controllers.payroll_calculation import PayrollCalculationController
from app.models.payroll_period import PayrollPeriod
from app.models.base import db
import logging

logger = logging.getLogger(__name__)


def generate_auto_payroll_summaries():
    """
    Tarea programada para generar automáticamente resúmenes de liquidación.
    Se ejecuta el último día de cada período a las 23:59.
    
    Para cada período que termina hoy:
    - Si el chofer tiene viajes en curso → estado 'calculation_pending'
    - Si el chofer tiene viajes sin tarifa → estado 'error'
    - Si todo está OK → estado 'pending_approval'
    """
    try:
        today = datetime.now().date()
        
        # Buscar períodos que terminan hoy
        periods = PayrollPeriod.query.filter(
            PayrollPeriod.end_date == today
        ).all()
        
        if not periods:
            logger.info(f"No hay períodos que terminen hoy ({today})")
            return
        
        logger.info(f"Generando resúmenes automáticos para {len(periods)} período(s) que terminan hoy")
        
        for period in periods:
            try:
                # Generar resúmenes automáticamente (is_manual=False)
                summaries = PayrollCalculationController.generate_summaries(
                    period_id=period.id,
                    driver_ids=None,  # Todos los choferes activos
                    is_manual=False
                )
                
                logger.info(
                    f"Período {period.start_date} - {period.end_date}: "
                    f"{len(summaries)} resúmenes generados"
                )
                
                # Registrar resúmenes por estado
                for summary in summaries:
                    logger.info(
                        f"  - Chofer {summary.driver_id}: {summary.status} "
                        f"(Total: ${summary.total_amount})"
                    )
                    
            except Exception as e:
                logger.error(f"Error generando resúmenes para período {period.id}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error en generación automática de resúmenes: {str(e)}")


def recalculate_pending_payroll_summaries(driver_id, period_id):
    """
    Recalcular resúmenes en estado 'calculation_pending' cuando se completa un viaje.
    
    Args:
        driver_id: ID del chofer
        period_id: ID del período
    """
    try:
        from app.models.payroll_summary import PayrollSummary
        
        # Buscar el resumen en calculation_pending para este chofer en este período
        summary = PayrollSummary.query.filter_by(
            period_id=period_id,
            driver_id=driver_id,
            status='calculation_pending'
        ).first()
        
        if not summary:
            logger.debug(
                f"No hay resumen en 'calculation_pending' para "
                f"chofer {driver_id} en período {period_id}"
            )
            return
        
        logger.info(
            f"Recalculando resumen en 'calculation_pending' para "
            f"chofer {driver_id} en período {period_id}"
        )
        
        # Obtener el período
        period = PayrollPeriod.query.get(period_id)
        if not period:
            logger.error(f"Período {period_id} no encontrado")
            return
        
        # Obtener el chofer
        from app.models.driver import Driver
        driver = Driver.query.get(driver_id)
        if not driver:
            logger.error(f"Chofer {driver_id} no encontrado")
            return
        
        # Eliminar el resumen anterior para regenerarlo
        db.session.delete(summary)
        db.session.flush()
        
        # Regenerar el resumen (is_manual=False para mantener como automático)
        new_summary = PayrollCalculationController._calculate_summary(
            period, driver, is_manual=False
        )
        
        db.session.commit()
        
        logger.info(
            f"Resumen recalculado para chofer {driver_id} en período {period_id}: "
            f"nuevo estado = {new_summary.status}"
        )
        
    except Exception as e:
        logger.error(
            f"Error recalculando resumen en 'calculation_pending' para "
            f"chofer {driver_id} en período {period_id}: {str(e)}"
        )
        db.session.rollback()


def start_scheduler(app):
    """
    Iniciar el scheduler de tareas programadas.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    scheduler = BackgroundScheduler()
    
    # Configurar la generación automática de resúmenes
    # Se ejecuta el último día de cada mes a las 23:59
    scheduler.add_job(
        func=generate_auto_payroll_summaries,
        trigger='cron',
        day='last',  # Último día del mes
        hour=23,
        minute=59,
        id='generate_auto_payroll_summaries',
        name='Generar resúmenes automáticos de liquidación',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        logger.info("Scheduler de tareas programadas iniciado correctamente")
        
        # Devolver el scheduler para poder detenerlo si es necesario
        return scheduler
    except Exception as e:
        logger.error(f"Error iniciando scheduler: {str(e)}")
        return None
