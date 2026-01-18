from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers.driver_truck import DriverTruckController
from ..utils import admin_required

driver_truck_bp = Blueprint('driver_truck', __name__, url_prefix='/driver-trucks')

@driver_truck_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required()
def get_driver_trucks():
    return DriverTruckController.get_all_driver_trucks()

@driver_truck_bp.route('/driver/<int:driver_id>/trucks', methods=['GET'])
@jwt_required()
def get_driver_trucks_by_driver(driver_id):
    """Obtiene todos los camiones de un conductor (solo admin o el mismo conductor)"""
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    # Solo admin o el propio conductor
    if not is_admin and current_user_id != driver_id:
        return {'error': 'No tienes permisos para ver esta información'}, 403
    
    return DriverTruckController.get_trucks_by_driver(driver_id)

@driver_truck_bp.route('/driver/<int:driver_id>/current-truck', methods=['GET'])
@jwt_required()
def get_current_truck_by_driver(driver_id):
    """Obtiene el camión actual de un conductor (el más reciente)"""
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    # Solo admin o el propio conductor
    if not is_admin and current_user_id != driver_id:
        return {'error': 'No tienes permisos para ver esta información'}, 403
    
    truck = DriverTruckController.get_current_truck_by_driver(driver_id)
    if truck:
        return jsonify(truck), 200
    else:
        return jsonify({'error': 'No hay camión asignado'}), 404

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_driver_truck(driver_truck_id):
    return DriverTruckController.get_driver_truck_by_id(driver_truck_id)

@driver_truck_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_driver_truck():
    return DriverTruckController.create_driver_truck(request.get_json())

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_driver_truck(driver_truck_id):
    return DriverTruckController.update_driver_truck(driver_truck_id, request.get_json())

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_driver_truck(driver_truck_id):
    return DriverTruckController.delete_driver_truck(driver_truck_id)
