"""Rutas para gestión de liquidaciones y cálculos."""
from flask import Blueprint, request, jsonify, send_file
from marshmallow import ValidationError
from app.controllers.payroll_calculation import PayrollCalculationController
from app.controllers.payroll_export import PayrollExportController
from app.schemas.payroll import (
    PayrollSummarySchema, GeneratePayrollSchema, PayrollDetailSchema,
    ApprovePayrollSchema, ExportPayrollSchema
)

payroll_summary_bp = Blueprint('payroll_summary', __name__, url_prefix='/api/payroll/summaries')

summary_schema = PayrollSummarySchema()
summaries_schema = PayrollSummarySchema(many=True)
generate_schema = GeneratePayrollSchema()
detail_schema = PayrollDetailSchema()
details_schema = PayrollDetailSchema(many=True)
approve_schema = ApprovePayrollSchema()
export_schema = ExportPayrollSchema()


@payroll_summary_bp.route('/generate', methods=['POST'])
def generate_summaries():
    """
    Generar resúmenes de liquidación.
    
    Tipos de generación:
    1. MANUAL (is_manual=True):
       - Genera resúmenes para todos los viajes FINALIZADOS del período
       - Ignora viajes en curso
       - Estado inicial: 'draft'
    
    2. AUTOMÁTICA (is_manual=False):
       - Se ejecuta el último día del período automáticamente
       - Valida si hay viajes en curso:
         • Si hay viajes en curso → estado 'calculation_pending' (recalculará cuando finalicen)
         • Si no hay viajes en curso → procede con el cálculo
       - Valida que todos los viajes tengan tarifa
         • Si algún viaje no tiene tarifa → estado 'error'
         • Si todo OK → estado 'pending_approval'
    
    Payload:
    {
        "period_id": int,
        "driver_ids": [int, ...] (opcional, si no se especifica calcula todos los activos),
        "is_manual": boolean (por defecto false)
    }
    """
    try:
        data = generate_schema.load(request.json)
        
        summaries = PayrollCalculationController.generate_summaries(
            period_id=data['period_id'],
            driver_ids=data.get('driver_ids'),
            is_manual=data.get('is_manual', False)
        )
        
        return jsonify({
            'success': True,
            'data': summaries_schema.dump(summaries),
            'message': f'{len(summaries)} resúmenes generados exitosamente'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        import traceback
        print(f"ERROR generando resúmenes: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('', methods=['GET'])
def get_all_summaries():
    """Obtener resúmenes con filtros."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        period_id = request.args.get('period_id', type=int)
        driver_id = request.args.get('driver_id', type=int)
        status = request.args.get('status')
        
        pagination = PayrollCalculationController.get_all_summaries(
            period_id=period_id,
            driver_id=driver_id,
            status=status,
            page=page,
            per_page=per_page
        )
        
        # Agregar datos del período y conductor a cada resumen
        summaries_data = []
        for summary in pagination.items:
            summary_dict = summary_schema.dump(summary)
            summary_dict['period_month'] = summary.period.month
            summary_dict['period_year'] = summary.period.year
            summary_dict['driver_name'] = f"{summary.driver.user.name} {summary.driver.user.surname}"
            summaries_data.append(summary_dict)
        
        return jsonify({
            'success': True,
            'data': summaries_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/<int:summary_id>', methods=['GET'])
def get_summary(summary_id):
    """Obtener un resumen específico con sus detalles."""
    try:
        summary, details = PayrollCalculationController.get_summary_details(summary_id)
        
        # Serializar summary y agregar datos del período y conductor
        summary_dict = summary_schema.dump(summary)
        summary_dict['period_month'] = summary.period.month
        summary_dict['period_year'] = summary.period.year
        summary_dict['driver_name'] = f"{summary.driver.user.name} {summary.driver.user.surname}"
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary_dict,
                'details': details_schema.dump(details)
            }
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/<int:summary_id>/approve', methods=['POST'])
def approve_summary(summary_id):
    """Aprobar un resumen de liquidación."""
    try:
        data = request.json or {}
        notes = data.get('notes')
        
        summary = PayrollCalculationController.approve_summary(summary_id, notes)
        
        return jsonify({
            'success': True,
            'data': summary_schema.dump(summary),
            'message': 'Resumen aprobado exitosamente'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/<int:summary_id>/recalculate', methods=['POST'])
def recalculate_summary(summary_id):
    """
    Recalcular un resumen existente.
    
    Útil cuando:
    - Se toca el botón "Recalcular resumen" manualmente
    - Se finaliza un viaje y necesita recalcularse un resumen en 'calculation_pending'
    
    Devuelve el resumen recalculado con todos sus detalles actualizados.
    """
    try:
        # Recalcular el resumen
        recalculated = PayrollCalculationController.recalculate_summary(summary_id)
        
        # Obtener detalles actualizados
        summary, details = PayrollCalculationController.get_summary_details(summary_id)
        
        # Serializar summary y agregar datos adicionales
        summary_dict = summary_schema.dump(summary)
        summary_dict['period_month'] = summary.period.month
        summary_dict['period_year'] = summary.period.year
        summary_dict['driver_name'] = f"{summary.driver.user.name} {summary.driver.user.surname}"
        
        return jsonify({
            'success': True,
            'data': {
                'summary': summary_dict,
                'details': details_schema.dump(details)
            },
            'message': 'Resumen recalculado exitosamente'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/by-driver/<int:driver_id>', methods=['GET'])
def get_summaries_by_driver(driver_id):
    """Obtener resúmenes de un chofer específico."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = PayrollCalculationController.get_all_summaries(
            driver_id=driver_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': summaries_schema.dump(pagination.items),
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/by-period/<int:period_id>', methods=['GET'])
def get_summaries_by_period(period_id):
    """Obtener resúmenes de un período específico."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = PayrollCalculationController.get_all_summaries(
            period_id=period_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': summaries_schema.dump(pagination.items),
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/<int:summary_id>/export', methods=['POST'])
def export_summary(summary_id):
    """Exportar resumen a Excel o PDF."""
    try:
        data = request.json or {}
        format_type = data.get('format', 'excel')
        
        if format_type == 'excel':
            filepath = PayrollExportController.export_to_excel(summary_id)
            message = 'Resumen exportado a Excel exitosamente'
        elif format_type == 'pdf':
            filepath = PayrollExportController.export_to_pdf(summary_id)
            message = 'Resumen exportado a PDF exitosamente'
        else:
            return jsonify({
                'success': False,
                'message': 'Formato no válido. Use "excel" o "pdf"'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'filepath': filepath,
                'format': format_type
            },
            'message': message
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_summary_bp.route('/<int:summary_id>/download', methods=['GET'])
def download_summary(summary_id):
    """Descargar archivo de exportación."""
    try:
        import os
        summary = PayrollCalculationController.get_summary(summary_id)
        
        if not summary.export_path:
            return jsonify({
                'success': False,
                'message': 'No hay archivo de exportación disponible'
            }), 404
        
        return send_file(
            summary.export_path,
            as_attachment=True,
            download_name=os.path.basename(summary.export_path)
        )
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
