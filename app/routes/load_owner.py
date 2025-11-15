from flask import Blueprint, request
from ..controllers.load_owner import LoadOwnerController

load_owner_bp = Blueprint('load_owner', __name__, url_prefix='/load-owners')

@load_owner_bp.route('/', methods=['GET'])
def get_load_owners():
    return LoadOwnerController.get_all_load_owners()

@load_owner_bp.route('/<int:load_owner_id>', methods=['GET'])
def get_load_owner(load_owner_id):
    return LoadOwnerController.get_load_owner_by_id(load_owner_id)

@load_owner_bp.route('/', methods=['POST'])
def create_load_owner():
    return LoadOwnerController.create_load_owner(request.get_json())

@load_owner_bp.route('/<int:load_owner_id>', methods=['PUT'])
def update_load_owner(load_owner_id):
    return LoadOwnerController.update_load_owner(load_owner_id, request.get_json())

@load_owner_bp.route('/<int:load_owner_id>', methods=['DELETE'])
def delete_load_owner(load_owner_id):
    return LoadOwnerController.delete_load_owner(load_owner_id)
