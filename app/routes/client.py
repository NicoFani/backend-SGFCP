from flask import Blueprint, request
from ..controllers.client import ClientController

client_bp = Blueprint('client', __name__, url_prefix='/clients')

@client_bp.route('/', methods=['GET'])
def get_clients():
    return ClientController.get_all_clients()

@client_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    return ClientController.get_client_by_id(client_id)

@client_bp.route('/', methods=['POST'])
def create_client():
    return ClientController.create_client(request.get_json())

@client_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    return ClientController.update_client(client_id, request.get_json())

@client_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    return ClientController.delete_client(client_id)
