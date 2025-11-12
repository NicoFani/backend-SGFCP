from flask import Blueprint, request
from ..controllers import TruckController

truck_bp = Blueprint('truck', __name__, url_prefix='/trucks')

# GET all trucks
@truck_bp.route('/', methods=['GET'])
def get_trucks():
    return TruckController.get_all_trucks()

# GET one truck
@truck_bp.route('/<int:truck_id>', methods=['GET'])
def get_truck(truck_id):
    return TruckController.get_truck_by_id(truck_id)

# CREATE truck
@truck_bp.route('/', methods=['POST'])
def create_truck():
    return TruckController.create_truck(request.get_json())

# UPDATE truck
@truck_bp.route('/<int:truck_id>', methods=['PUT'])
def update_truck(truck_id):
    return TruckController.update_truck(truck_id, request.get_json())

# DELETE truck
@truck_bp.route('/<int:truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    return TruckController.delete_truck(truck_id)