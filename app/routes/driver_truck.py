from flask import Blueprint, request
from ..controllers.driver_truck import DriverTruckController

driver_truck_bp = Blueprint('driver_truck', __name__, url_prefix='/driver-trucks')

@driver_truck_bp.route('/', methods=['GET'])
def get_driver_trucks():
    return DriverTruckController.get_all_driver_trucks()

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['GET'])
def get_driver_truck(driver_truck_id):
    return DriverTruckController.get_driver_truck_by_id(driver_truck_id)

@driver_truck_bp.route('/', methods=['POST'])
def create_driver_truck():
    return DriverTruckController.create_driver_truck(request.get_json())

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['PUT'])
def update_driver_truck(driver_truck_id):
    return DriverTruckController.update_driver_truck(driver_truck_id, request.get_json())

@driver_truck_bp.route('/<int:driver_truck_id>', methods=['DELETE'])
def delete_driver_truck(driver_truck_id):
    return DriverTruckController.delete_driver_truck(driver_truck_id)
