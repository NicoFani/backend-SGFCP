"""Rutas para gestión de mínimo garantizado."""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.controllers.minimum_guaranteed import MinimumGuaranteedController
from app.schemas.payroll import MinimumGuaranteedHistorySchema

minimum_guaranteed_bp = Blueprint('minimum_guaranteed', __name__)
schema = MinimumGuaranteedHistorySchema()


@minimum_guaranteed_bp.route('/minimum-guaranteed', methods=['POST'])
def create_minimum_guaranteed():
    """Crear nuevo registro de mínimo garantizado."""
    try:
        data = schema.load(request.json)
        record = MinimumGuaranteedController.create(
            driver_id=data['driver_id'],
            minimum_guaranteed=data['minimum_guaranteed'],
            effective_from=data.get('effective_from')  # Opcional
        )
        return jsonify(schema.dump(record)), 201
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed/<int:record_id>', methods=['GET'])
def get_minimum_guaranteed(record_id):
    """Obtener registro por ID."""
    try:
        record = MinimumGuaranteedController.get_by_id(record_id)
        if not record:
            return jsonify({'error': 'Registro no encontrado'}), 404
        return jsonify(schema.dump(record)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed', methods=['GET'])
def get_all_minimum_guaranteed():
    """Obtener todos los registros, opcionalmente filtrados por chofer."""
    try:
        driver_id = request.args.get('driver_id', type=int)
        records = MinimumGuaranteedController.get_all(driver_id=driver_id)
        return jsonify(schema.dump(records, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed/driver/<int:driver_id>/current', methods=['GET'])
def get_current_minimum_guaranteed(driver_id):
    """Obtener el mínimo garantizado vigente para un chofer."""
    try:
        record = MinimumGuaranteedController.get_current(driver_id)
        if not record:
            return jsonify({'error': 'No se encontró mínimo garantizado vigente para el chofer'}), 404
        return jsonify(schema.dump(record)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed/driver/<int:driver_id>/at-date', methods=['GET'])
def get_minimum_guaranteed_at_date(driver_id):
    """Obtener el mínimo garantizado vigente en una fecha específica."""
    try:
        date_str = request.args.get('date', required=True)
        from datetime import datetime
        reference_date = datetime.fromisoformat(date_str)
        
        record = MinimumGuaranteedController.get_at_date(driver_id, reference_date)
        if not record:
            return jsonify({'error': 'No se encontró mínimo garantizado para la fecha especificada'}), 404
        return jsonify(schema.dump(record)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed/<int:record_id>', methods=['PUT'])
def update_minimum_guaranteed(record_id):
    """Actualizar registro."""
    try:
        from app.schemas.payroll import MinimumGuaranteedHistorySchema
        update_schema = MinimumGuaranteedHistorySchema(partial=True)
        data = update_schema.load(request.json)
        
        record = MinimumGuaranteedController.update(record_id, **data)
        return jsonify(schema.dump(record)), 200
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@minimum_guaranteed_bp.route('/minimum-guaranteed/<int:record_id>', methods=['DELETE'])
def delete_minimum_guaranteed(record_id):
    """Eliminar registro."""
    try:
        MinimumGuaranteedController.delete(record_id)
        return jsonify({'message': 'Registro eliminado exitosamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
