"""Rutas para gestión de configuración de liquidación."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.controllers.payroll_settings import PayrollSettingsController
from app.schemas.payroll import PayrollSettingsSchema

payroll_settings_bp = Blueprint('payroll_settings', __name__, url_prefix='/api/payroll/settings')

settings_schema = PayrollSettingsSchema()
settings_list_schema = PayrollSettingsSchema(many=True)


@payroll_settings_bp.route('', methods=['GET'])
def get_current_settings():
    """Obtener la configuración vigente actual."""
    try:
        settings = PayrollSettingsController.get_current_settings()
        return jsonify({
            'success': True,
            'data': settings_schema.dump(settings)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_settings_bp.route('', methods=['PUT'])
def update_settings():
    """Actualizar la configuración (crea nuevo registro histórico)."""
    try:
        data = settings_schema.load(request.json, partial=True)
        
        settings = PayrollSettingsController.update_settings(
            guaranteed_minimum=data.get('guaranteed_minimum'),
            default_commission_percentage=data.get('default_commission_percentage'),
            auto_generation_day=data.get('auto_generation_day')
        )
        
        return jsonify({
            'success': True,
            'data': settings_schema.dump(settings),
            'message': 'Configuración actualizada exitosamente'
        }), 200
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_settings_bp.route('/history', methods=['GET'])
def get_settings_history():
    """Obtener historial de configuraciones."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = PayrollSettingsController.get_settings_history(
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': settings_list_schema.dump(pagination.items),
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
