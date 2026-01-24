"""Rutas para gestión de otros conceptos de liquidación."""
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.controllers.payroll_other_item import PayrollOtherItemController
from app.schemas.payroll import PayrollOtherItemSchema

payroll_other_item_bp = Blueprint('payroll_other_item', __name__)
schema = PayrollOtherItemSchema()


@payroll_other_item_bp.route('/payroll-other-items', methods=['POST'])
@jwt_required()
def create_other_item():
    """Crear nuevo concepto."""
    try:
        user_id = get_jwt_identity()
        data = schema.load(request.json)
        item = PayrollOtherItemController.create(
            driver_id=data['driver_id'],
            period_id=data['period_id'],
            item_type=data['item_type'],
            description=data['description'],
            amount=data['amount'],
            date=date.today(),
            created_by=user_id,
            reference=data.get('reference'),
            receipt_url=data.get('receipt_url')
        )
        return jsonify(schema.dump(item)), 201
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items/<int:item_id>', methods=['GET'])
def get_other_item(item_id):
    """Obtener concepto por ID."""
    try:
        item = PayrollOtherItemController.get_by_id(item_id)
        if not item:
            return jsonify({'error': 'Concepto no encontrado'}), 404
        return jsonify(schema.dump(item)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items', methods=['GET'])
def get_all_other_items():
    """Obtener todos los conceptos con filtros opcionales."""
    try:
        driver_id = request.args.get('driver_id', type=int)
        period_id = request.args.get('period_id', type=int)
        item_type = request.args.get('item_type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = PayrollOtherItemController.get_all(
            driver_id=driver_id,
            period_id=period_id,
            item_type=item_type,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'items': schema.dump(result.items, many=True),
            'total': result.total,
            'page': result.page,
            'per_page': result.per_page,
            'pages': result.pages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items/period/<int:period_id>/driver/<int:driver_id>', methods=['GET'])
def get_other_items_by_period_and_driver(period_id, driver_id):
    """Obtener todos los conceptos de un chofer en un período."""
    try:
        items = PayrollOtherItemController.get_by_period_and_driver(period_id, driver_id)
        return jsonify(schema.dump(items, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items/period/<int:period_id>/driver/<int:driver_id>/summary', methods=['GET'])
def get_other_items_summary(period_id, driver_id):
    """Obtener resumen de conceptos por tipo para un chofer en un período."""
    try:
        summary = PayrollOtherItemController.get_summary_by_type(period_id, driver_id)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items/<int:item_id>', methods=['PUT'])
def update_other_item(item_id):
    """Actualizar concepto."""
    try:
        update_schema = PayrollOtherItemSchema(partial=True)
        data = update_schema.load(request.json)
        
        item = PayrollOtherItemController.update(item_id, **data)
        return jsonify(schema.dump(item)), 200
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payroll_other_item_bp.route('/payroll-other-items/<int:item_id>', methods=['DELETE'])
def delete_other_item(item_id):
    """Eliminar concepto."""
    try:
        PayrollOtherItemController.delete(item_id)
        return jsonify({'message': 'Concepto eliminado exitosamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
