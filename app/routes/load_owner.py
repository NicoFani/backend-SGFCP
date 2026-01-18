from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..controllers.load_owner import LoadOwnerController
from ..utils import admin_required

load_owner_bp = Blueprint('load_owner', __name__, url_prefix='/load-owners')

@load_owner_bp.route('/', methods=['GET'])
@jwt_required()
def get_load_owners():
    return LoadOwnerController.get_all_load_owners()

@load_owner_bp.route('/<int:load_owner_id>', methods=['GET'])
@jwt_required()
def get_load_owner(load_owner_id):
    return LoadOwnerController.get_load_owner_by_id(load_owner_id)

@load_owner_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_load_owner():
    return LoadOwnerController.create_load_owner(request.get_json())

@load_owner_bp.route('/<int:load_owner_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_load_owner(load_owner_id):
    return LoadOwnerController.update_load_owner(load_owner_id, request.get_json())

@load_owner_bp.route('/<int:load_owner_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_load_owner(load_owner_id):
    return LoadOwnerController.delete_load_owner(load_owner_id)
