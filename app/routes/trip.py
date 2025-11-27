from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers import TripController
from ..utils import admin_required

trip_bp = Blueprint('trip', __name__, url_prefix='/trips')

# GET all trips (filtrados por conductor si no es admin)
@trip_bp.route('/', methods=['GET'])
@jwt_required()
def get_trips():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return TripController.get_all_trips(current_user_id, is_admin)

# GET one trip (solo el propio viaje o admin)
@trip_bp.route('/<int:trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return TripController.get_trip_by_id(trip_id, current_user_id, is_admin)

# CREATE trip (solo admin)
@trip_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_trip():
    return TripController.create_trip(request.get_json())

# UPDATE trip (admin puede todo, chofer solo puede actualizar sus viajes y ciertos campos)
@trip_bp.route('/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return TripController.update_trip(trip_id, request.get_json(), current_user_id, is_admin)

# DELETE trip (solo admin)
@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_trip(trip_id):
    return TripController.delete_trip(trip_id)

# GET trips by driver
@trip_bp.route('/driver/<int:driver_id>', methods=['GET'])
def get_trips_by_driver(driver_id):
    return TripController.get_trips_by_driver(driver_id)

# GET trips by state
@trip_bp.route('/state/<string:state>', methods=['GET'])
def get_trips_by_state(state):
    return TripController.get_trips_by_state(state)