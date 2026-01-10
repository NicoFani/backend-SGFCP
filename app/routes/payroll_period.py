"""Rutas para gestión de períodos de liquidación."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.controllers.payroll_period import PayrollPeriodController
from app.schemas.payroll import PayrollPeriodSchema, ClosePeriodSchema

payroll_period_bp = Blueprint('payroll_period', __name__, url_prefix='/api/payroll/periods')

period_schema = PayrollPeriodSchema()
periods_schema = PayrollPeriodSchema(many=True)
close_schema = ClosePeriodSchema()


@payroll_period_bp.route('', methods=['POST'])
def create_period():
    """Crear un nuevo período de liquidación."""
    try:
        data = period_schema.load(request.json)
        period = PayrollPeriodController.create_period(
            year=data['year'],
            month=data['month'],
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        return jsonify({
            'success': True,
            'data': period_schema.dump(period),
            'message': 'Período creado exitosamente'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('', methods=['GET'])
def get_all_periods():
    """Obtener todos los períodos con paginación."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        pagination = PayrollPeriodController.get_all_periods(
            page=page,
            per_page=per_page,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': periods_schema.dump(pagination.items),
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('/<int:period_id>', methods=['GET'])
def get_period(period_id):
    """Obtener un período específico."""
    try:
        period = PayrollPeriodController.get_period(period_id)
        return jsonify({
            'success': True,
            'data': period_schema.dump(period)
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('/current', methods=['GET'])
def get_current_period():
    """Obtener el período actual."""
    try:
        period = PayrollPeriodController.get_current_period()
        return jsonify({
            'success': True,
            'data': period_schema.dump(period)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('/<int:period_id>/close', methods=['POST'])
def close_period(period_id):
    """Cerrar un período de liquidación."""
    try:
        data = request.json or {}
        force = data.get('force', False)
        
        period = PayrollPeriodController.close_period(period_id, force=force)
        return jsonify({
            'success': True,
            'data': period_schema.dump(period),
            'message': 'Período cerrado exitosamente'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('/<int:period_id>/reopen', methods=['PUT'])
def reopen_period(period_id):
    """Reabrir un período para realizar ajustes."""
    try:
        period = PayrollPeriodController.reopen_period(period_id)
        return jsonify({
            'success': True,
            'data': period_schema.dump(period),
            'message': 'Período reabierto para ajustes'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_period_bp.route('/<int:period_id>/check-trips', methods=['GET'])
def check_trips_in_progress(period_id):
    """Verificar si hay viajes en curso en el período."""
    try:
        has_trips = PayrollPeriodController.check_trips_in_progress(period_id)
        return jsonify({
            'success': True,
            'data': {
                'has_trips_in_progress': has_trips
            }
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
