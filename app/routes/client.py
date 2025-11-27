from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..controllers.client import ClientController
from ..utils import admin_required

client_bp = Blueprint('client', __name__, url_prefix='/clients')

@client_bp.route('/', methods=['GET'])
@jwt_required()
def get_clients():
    return ClientController.get_all_clients()

@client_bp.route('/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    return ClientController.get_client_by_id(client_id)

@client_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_client():
    return ClientController.create_client(request.get_json())

@client_bp.route('/<int:client_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_client(client_id):
    return ClientController.update_client(client_id, request.get_json())

@client_bp.route('/<int:client_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_client(client_id):
    return ClientController.delete_client(client_id)
