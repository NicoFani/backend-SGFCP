from flask import Blueprint, request
from ..controllers import TripController

trip_bp = Blueprint('trip', __name__, url_prefix='/trips')

# GET all trips
@trip_bp.route('/', methods=['GET'])
def get_trips():
    return TripController.get_all_trips()

# GET one trip
@trip_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    return TripController.get_trip_by_id(trip_id)

# CREATE trip
@trip_bp.route('/', methods=['POST'])
def create_trip():
    return TripController.create_trip(request.get_json())

# UPDATE trip
@trip_bp.route('/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    return TripController.update_trip(trip_id, request.get_json())

# DELETE trip
@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
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