"""Rutas para gestión de ajustes retroactivos."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.controllers.payroll_adjustment import PayrollAdjustmentController
from app.schemas.payroll import PayrollAdjustmentSchema

payroll_adjustment_bp = Blueprint('payroll_adjustment', __name__, url_prefix='/api/payroll/adjustments')

adjustment_schema = PayrollAdjustmentSchema()
adjustments_schema = PayrollAdjustmentSchema(many=True)


@payroll_adjustment_bp.route('', methods=['POST'])
def create_adjustment():
    """Crear un ajuste retroactivo."""
    try:
        data = adjustment_schema.load(request.json)
        
        # TODO: Obtener el usuario actual del token JWT
        created_by = request.json.get('created_by', 1)  # Temporal
        
        adjustment = PayrollAdjustmentController.create_adjustment(
            origin_period_id=data['origin_period_id'],
            driver_id=data['driver_id'],
            amount=data['amount'],
            description=data['description'],
            adjustment_type=data['adjustment_type'],
            created_by=created_by,
            trip_id=data.get('trip_id'),
            expense_id=data.get('expense_id')
        )
        
        return jsonify({
            'success': True,
            'data': adjustment_schema.dump(adjustment),
            'message': 'Ajuste creado exitosamente'
        }), 201
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_adjustment_bp.route('', methods=['GET'])
def get_all_adjustments():
    """Obtener ajustes con filtros."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        origin_period_id = request.args.get('origin_period_id', type=int)
        driver_id = request.args.get('driver_id', type=int)
        is_applied = request.args.get('is_applied')
        
        pagination = PayrollAdjustmentController.get_all_adjustments(
            origin_period_id=origin_period_id,
            driver_id=driver_id,
            is_applied=is_applied,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': adjustments_schema.dump(pagination.items),
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_adjustment_bp.route('/<int:adjustment_id>', methods=['GET'])
def get_adjustment(adjustment_id):
    """Obtener un ajuste específico."""
    try:
        adjustment = PayrollAdjustmentController.get_adjustment(adjustment_id)
        return jsonify({
            'success': True,
            'data': adjustment_schema.dump(adjustment)
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_adjustment_bp.route('/<int:adjustment_id>', methods=['PUT'])
def update_adjustment(adjustment_id):
    """Actualizar un ajuste retroactivo."""
    try:
        data = request.json or {}
        
        adjustment = PayrollAdjustmentController.update_adjustment(
            adjustment_id=adjustment_id,
            amount=data.get('amount'),
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'data': adjustment_schema.dump(adjustment),
            'message': 'Ajuste actualizado exitosamente'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_adjustment_bp.route('/<int:adjustment_id>', methods=['DELETE'])
def delete_adjustment(adjustment_id):
    """Eliminar un ajuste retroactivo."""
    try:
        PayrollAdjustmentController.delete_adjustment(adjustment_id)
        return jsonify({
            'success': True,
            'message': 'Ajuste eliminado exitosamente'
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500


@payroll_adjustment_bp.route('/pending/<int:driver_id>', methods=['GET'])
def get_pending_adjustments(driver_id):
    """Obtener ajustes pendientes de un chofer."""
    try:
        adjustments = PayrollAdjustmentController.get_pending_adjustments_for_driver(driver_id)
        return jsonify({
            'success': True,
            'data': adjustments_schema.dump(adjustments)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500
