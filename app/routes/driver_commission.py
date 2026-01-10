"""Rutas para gestión de historial de comisión de choferes."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.controllers.driver_commission import DriverCommissionController
from app.schemas.payroll import DriverCommissionHistorySchema

driver_commission_bp = Blueprint('driver_commission', __name__, url_prefix='/api/drivers')

commission_schema = DriverCommissionHistorySchema()
commissions_schema = DriverCommissionHistorySchema(many=True)


@driver_commission_bp.route('/<int:driver_id>/commission', methods=['POST'])
def set_driver_commission(driver_id):
    """Establecer el porcentaje de comisión de un chofer."""
    try:
        data = commission_schema.load(request.json)
        
        commission_record = DriverCommissionController.set_driver_commission(
            driver_id=driver_id,
            commission_percentage=data['commission_percentage'],
            effective_from=data.get('effective_from')
        )
        
        return jsonify({
            'success': True,
            'data': commission_schema.dump(commission_record),
            'message': 'Comisión establecida exitosamente'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@driver_commission_bp.route('/<int:driver_id>/commission/current', methods=['GET'])
def get_current_commission(driver_id):
    """Obtener el porcentaje de comisión actual del chofer."""
    try:
        commission_pct = DriverCommissionController.get_driver_current_commission(driver_id)
        
        return jsonify({
            'success': True,
            'data': {
                'driver_id': driver_id,
                'commission_percentage': str(commission_pct)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@driver_commission_bp.route('/<int:driver_id>/commission/history', methods=['GET'])
def get_commission_history(driver_id):
    """Obtener historial de comisiones del chofer."""
    try:
        history = DriverCommissionController.get_driver_commission_history(driver_id)
        
        return jsonify({
            'success': True,
            'data': commissions_schema.dump(history)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
