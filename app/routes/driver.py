from flask import Blueprint, request
from ..controllers import DriverController

driver_bp = Blueprint('driver', __name__, url_prefix='/drivers')

# GET all drivers
@driver_bp.route('/', methods=['GET'])
def get_drivers():
    return DriverController.get_all_drivers()

# GET one driver
@driver_bp.route('/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    return DriverController.get_driver_by_id(driver_id)

# CREATE driver
@driver_bp.route('/', methods=['POST'])
def create_driver():
    return DriverController.create_driver(request.get_json())

# UPDATE driver
@driver_bp.route('/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    return DriverController.update_driver(driver_id, request.get_json())

# DELETE driver
@driver_bp.route('/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    return DriverController.delete_driver(driver_id)
