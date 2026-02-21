"""Tareas programadas para la aplicación SGFCP."""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import current_app
from app.controllers.payroll_calculation import PayrollCalculationController
from app.controllers.payroll_export import PayrollExportController
from app.models.payroll_period import PayrollPeriod
from app.models.base import db
from app.utils.brevo_email import send_brevo_email
import logging
import os

logger = logging.getLogger(__name__)

# Variable global para almacenar la instancia de la app
_flask_app = None


def _send_payroll_email(app, period, summaries):
    """
    Enviar email con los resúmenes de liquidación generados automáticamente.
    
    Args:
        app: Instancia de la aplicación Flask
        period: Objeto PayrollPeriod
        summaries: Lista de objetos PayrollSummary generados
    """
    try:
        # Obtener configuración de Brevo
        api_key = app.config.get('BREVO_API_KEY', '')
        sender_email = app.config.get('BREVO_SENDER_EMAIL', '')
        sender_name = app.config.get('BREVO_SENDER_NAME', 'SGFCP')
        recipients_str = app.config.get('BREVO_ACCOUNTING_RECIPIENTS', '')
        
        if not recipients_str:
            logger.warning("No hay destinatarios configurados para envío de resúmenes")
            return
        
        recipients = [email.strip() for email in recipients_str.split(',')]
        
        # Separar resúmenes por estado
        pending_approval = []
        calculation_pending = []
        error_summaries = []
        other_statuses = []
        
        for summary in summaries:
            if summary.status == 'pending_approval':
                pending_approval.append(summary)
            elif summary.status == 'calculation_pending':
                calculation_pending.append(summary)
            elif summary.status == 'error':
                error_summaries.append(summary)
            else:
                other_statuses.append(summary)
        
        # Exportar resúmenes en pending_approval a Excel
        attachment_paths = []
        for summary in pending_approval:
            try:
                excel_path = PayrollExportController.export_to_excel(summary.id)
                attachment_paths.append(excel_path)
                logger.info(f"Excel generado para resumen {summary.id}: {excel_path}")
            except Exception as e:
                logger.error(f"Error generando Excel para resumen {summary.id}: {str(e)}")
        
        # Construir contenido HTML del email
        period_name = f"{period.month:02d}/{period.year}"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #366092; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; }}
                .table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                .table th {{ background-color: #B4C7E7; padding: 10px; text-align: left; border: 1px solid #ddd; }}
                .table td {{ padding: 8px; border: 1px solid #ddd; }}
                .status-pending {{ color: #0066cc; font-weight: bold; }}
                .status-error {{ color: #cc0000; font-weight: bold; }}
                .status-calculation {{ color: #ff8800; font-weight: bold; }}
                .total {{ font-weight: bold; font-size: 1.1em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Resúmenes de Liquidación - Período {period_name}</h1>
            </div>
            
            <div class="section">
                <p>Se han generado automáticamente los resúmenes de liquidación para el período <strong>{period_name}</strong>.</p>
            </div>
        """
        
        # Resúmenes pendientes de aprobación (adjuntos)
        if pending_approval:
            html_content += f"""
            <div class="section">
                <h2>✓ Resúmenes Listos para Aprobación ({len(pending_approval)})</h2>
                <p>Los siguientes resúmenes están adjuntos en formato Excel:</p>
                <table class="table">
                    <tr>
                        <th>ID</th>
                        <th>Chofer</th>
                        <th>Total</th>
                    </tr>
            """
            for summary in pending_approval:
                driver_name = f"{summary.driver.user.name} {summary.driver.user.surname}"
                total = f"${summary.total_amount:,.2f}"
                html_content += f"""
                    <tr>
                        <td>{summary.id}</td>
                        <td>{driver_name}</td>
                        <td class="total">{total}</td>
                    </tr>
                """
            html_content += """
                </table>
            </div>
            """
        
        # Resúmenes en cálculo pendiente
        if calculation_pending:
            html_content += f"""
            <div class="section">
                <h2>⏳ Resúmenes en Espera ({len(calculation_pending)})</h2>
                <p>Los siguientes resúmenes están pendientes de cálculo porque hay viajes en curso:</p>
                <table class="table">
                    <tr>
                        <th>ID</th>
                        <th>Chofer</th>
                        <th>Motivo</th>
                    </tr>
            """
            for summary in calculation_pending:
                driver_name = f"{summary.driver.user.name} {summary.driver.user.surname}"
                reason = summary.error_message or "Viajes en curso"
                html_content += f"""
                    <tr>
                        <td>{summary.id}</td>
                        <td>{driver_name}</td>
                        <td class="status-calculation">{reason}</td>
                    </tr>
                """
            html_content += """
                </table>
                <p><em>Estos resúmenes se calcularán automáticamente cuando finalicen los viajes en curso.</em></p>
            </div>
            """
        
        # Resúmenes con error
        if error_summaries:
            html_content += f"""
            <div class="section">
                <h2>⚠ Resúmenes con Error ({len(error_summaries)})</h2>
                <p>Los siguientes resúmenes tienen errores y requieren atención:</p>
                <table class="table">
                    <tr>
                        <th>ID</th>
                        <th>Chofer</th>
                        <th>Error</th>
                    </tr>
            """
            for summary in error_summaries:
                driver_name = f"{summary.driver.user.name} {summary.driver.user.surname}"
                error_msg = summary.error_message or "Error de cálculo"
                html_content += f"""
                    <tr>
                        <td>{summary.id}</td>
                        <td>{driver_name}</td>
                        <td class="status-error">{error_msg}</td>
                    </tr>
                """
            html_content += """
                </table>
            </div>
            """
        
        # Resumen final
        html_content += f"""
            <div class="section">
                <h3>Resumen Total</h3>
                <ul>
                    <li><strong>{len(pending_approval)}</strong> resúmenes listos para aprobación (adjuntos)</li>
                    <li><strong>{len(calculation_pending)}</strong> resúmenes en espera de cálculo</li>
                    <li><strong>{len(error_summaries)}</strong> resúmenes con errores</li>
                    <li><strong>{len(summaries)}</strong> resúmenes generados en total</li>
                </ul>
            </div>
            
            <div class="section">
                <p>Ingresá al sistema para revisar y aprobar los resúmenes.</p>
            </div>
        </body>
        </html>
        """
        
        # Enviar email
        subject = f"Resúmenes de Liquidación - Período {period_name}"
        success, message = send_brevo_email(
            api_key=api_key,
            sender_email=sender_email,
            sender_name=sender_name,
            recipients=recipients,
            subject=subject,
            html_content=html_content,
            attachment_paths=attachment_paths
        )
        
        if success:
            logger.info(f"Email de resúmenes enviado exitosamente a {', '.join(recipients)}")
        else:
            logger.error(f"Error enviando email de resúmenes: {message}")
        
        # Limpiar archivos temporales de Excel después de enviar
        for path in attachment_paths:
            try:
                if os.path.exists(path):
                    # No eliminar, mantener para registro
                    pass
            except Exception as e:
                logger.error(f"Error limpiando archivo {path}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error en _send_payroll_email: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def generate_auto_payroll_summaries():
    """
    Tarea programada para generar automáticamente resúmenes de liquidación.
    Se ejecuta el último día de cada período a las 23:59.
    
    Para cada período que termina hoy:
    - Si el chofer tiene viajes en curso → estado 'calculation_pending'
    - Si el chofer tiene viajes sin tarifa → estado 'error'
    - Si todo está OK → estado 'pending_approval'
    
    Después de generar los resúmenes, envía un email con:
    - Excel de los resúmenes en 'pending_approval'
    - Lista de resúmenes en otros estados (calculation_pending, error)
    """
    if not _flask_app:
        logger.error("No hay instancia de Flask disponible para ejecutar el scheduler")
        return
    
    with _flask_app.app_context():
        try:
            # SIMULACIÓN: Cambiado para probar generación automática
            # today = datetime.now().date()
            from datetime import date
            today = date(2026, 2, 28)  # Simular que es el último día de febrero
            
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
                    
                    # Enviar email con los resúmenes
                    logger.info(f"Enviando email con resúmenes del período {period.id}")
                    _send_payroll_email(_flask_app, period, summaries)
                        
                except Exception as e:
                    logger.error(f"Error generando resúmenes para período {period.id}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    
        except Exception as e:
            logger.error(f"Error en generación automática de resúmenes: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())


def recalculate_pending_payroll_summaries(driver_id, period_id):
    """
    Recalcular resúmenes en estado 'calculation_pending' cuando se completa un viaje.
    
    Args:
        driver_id: ID del chofer
        period_id: ID del período
    """
    if not _flask_app:
        logger.error("No hay instancia de Flask disponible para recalcular resúmenes")
        return
    
    with _flask_app.app_context():
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
            
            # Recalcular en el mismo registro para conservar el ID y evitar 404 en frontend
            new_summary = PayrollCalculationController.recalculate_summary(summary.id)
            
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
    global _flask_app
    _flask_app = app
    
    scheduler = BackgroundScheduler()
    
    # Configurar la generación automática de resúmenes
    # SIMULACIÓN: Ejecutar en 30 segundos para probar
    # Producción: Se ejecuta el último día de cada mes a las 23:59
    scheduler.add_job(
        func=generate_auto_payroll_summaries,
        trigger='date',  # Ejecutar una vez en una fecha específica
        run_date=datetime.now() + timedelta(seconds=30),  # En 30 segundos
        id='generate_auto_payroll_summaries',
        name='Generar resúmenes automáticos de liquidación (SIMULACIÓN)',
        replace_existing=True
    )
    # Original (descomentar para producción):
    # scheduler.add_job(
    #     func=generate_auto_payroll_summaries,
    #     trigger='cron',
    #     day='last',  # Último día del mes
    #     hour=23,
    #     minute=59,
    #     id='generate_auto_payroll_summaries',
    #     name='Generar resúmenes automáticos de liquidación',
    #     replace_existing=True
    # )
    
    try:
        scheduler.start()
        logger.info("Scheduler de tareas programadas iniciado correctamente")
        
        # Devolver el scheduler para poder detenerlo si es necesario
        return scheduler
    except Exception as e:
        logger.error(f"Error iniciando scheduler: {str(e)}")
        return None
