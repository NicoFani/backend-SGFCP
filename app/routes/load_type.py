from flask import Blueprint, request, jsonify
from app.controllers import load_type as load_type_controller

load_type_bp = Blueprint('load_type', __name__)

@load_type_bp.route('/load-types', methods=['GET'])
def get_all_load_types():
    """Obtener todos los tipos de carga"""
    try:
        load_types = load_type_controller.get_all_load_types()
        return jsonify(load_types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@load_type_bp.route('/load-types/<int:load_type_id>', methods=['GET'])
def get_load_type(load_type_id):
    """Obtener un tipo de carga por ID"""
    try:
        load_type = load_type_controller.get_load_type(load_type_id)
        if load_type is None:
            return jsonify({'error': 'Tipo de carga no encontrado'}), 404
        return jsonify(load_type), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@load_type_bp.route('/load-types', methods=['POST'])
def create_load_type():
    """Crear un nuevo tipo de carga"""
    try:
        data = request.get_json()
        load_type = load_type_controller.create_load_type(data)
        return jsonify(load_type), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@load_type_bp.route('/load-types/<int:load_type_id>', methods=['PUT'])
def update_load_type(load_type_id):
    """Actualizar un tipo de carga"""
    try:
        data = request.get_json()
        load_type = load_type_controller.update_load_type(load_type_id, data)
        if load_type is None:
            return jsonify({'error': 'Tipo de carga no encontrado'}), 404
        return jsonify(load_type), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@load_type_bp.route('/load-types/<int:load_type_id>', methods=['DELETE'])
def delete_load_type(load_type_id):
    """Eliminar un tipo de carga"""
    try:
        result = load_type_controller.delete_load_type(load_type_id)
        if result is None:
            return jsonify({'error': 'Tipo de carga no encontrado'}), 404
        return jsonify({'message': 'Tipo de carga eliminado exitosamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
