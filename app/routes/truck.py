from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..controllers import TruckController
from ..utils import admin_required

truck_bp = Blueprint('truck', __name__, url_prefix='/trucks')

# GET all trucks (todos pueden ver)
@truck_bp.route('/', methods=['GET'])
@jwt_required()
def get_trucks():
    return TruckController.get_all_trucks()

# GET one truck (todos pueden ver)
@truck_bp.route('/<int:truck_id>', methods=['GET'])
@jwt_required()
def get_truck(truck_id):
    return TruckController.get_truck_by_id(truck_id)

# CREATE truck (solo admin)
@truck_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_truck():
    return TruckController.create_truck(request.get_json())

# UPDATE truck (solo admin)
@truck_bp.route('/<int:truck_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_truck(truck_id):
    return TruckController.update_truck(truck_id, request.get_json())

# DELETE truck (solo admin)
@truck_bp.route('/<int:truck_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_truck(truck_id):
    return TruckController.delete_truck(truck_id)

# GET current driver for a truck
@truck_bp.route('/<int:truck_id>/current-driver', methods=['GET'])
@jwt_required()
def get_truck_current_driver(truck_id):
    return TruckController.get_truck_current_driver(truck_id)