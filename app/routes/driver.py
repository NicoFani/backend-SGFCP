from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers import DriverController
from ..utils import admin_required, owner_or_admin_required

driver_bp = Blueprint('driver', __name__, url_prefix='/drivers')

# GET all drivers (solo admin puede ver todos, conductores solo su info)
@driver_bp.route('/', methods=['GET'])
@jwt_required()
def get_drivers():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return DriverController.get_all_drivers(current_user_id, is_admin)

# GET all drivers with truck assignment status (para selector de camiones)
@driver_bp.route('/truck-status', methods=['GET'])
@jwt_required()
@admin_required()
def get_drivers_with_truck_status():
    return DriverController.get_drivers_with_truck_status()

# GET one driver (solo el propio conductor o admin)
@driver_bp.route('/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_driver(driver_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    # Solo admin o el propio conductor
    if not is_admin and current_user_id != driver_id:
        return {'error': 'No tienes permisos para ver este conductor'}, 403
    
    return DriverController.get_driver_by_id(driver_id)

# CREATE driver (solo admin)
@driver_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_driver():
    return DriverController.create_driver(request.get_json())

# CREATE driver completo (usuario + driver) - solo admin
@driver_bp.route('/complete', methods=['POST'])
@jwt_required()
@admin_required()
def create_driver_complete():
    return DriverController.create_driver_complete(request.get_json())

# UPDATE driver (solo el propio conductor o admin)
@driver_bp.route('/<int:driver_id>', methods=['PUT'])
@jwt_required()
def update_driver(driver_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    # Solo admin o el propio conductor
    if not is_admin and current_user_id != driver_id:
        return {'error': 'No tienes permisos para actualizar este conductor'}, 403
    
    return DriverController.update_driver(driver_id, request.get_json())

# UPDATE driver basic data (datos básicos) - solo admin
@driver_bp.route('/<int:driver_id>/basic', methods=['PUT'])
@jwt_required()
@admin_required()
def update_driver_basic(driver_id):
    return DriverController.update_driver_basic_data(driver_id, request.get_json())

# DELETE driver (solo admin)
@driver_bp.route('/<int:driver_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_driver(driver_id):
    return DriverController.delete_driver(driver_id)
