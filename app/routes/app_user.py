from flask import Blueprint, request
from ..controllers.app_user import AppUserController

app_user_bp = Blueprint('app_user', __name__, url_prefix='/users')

@app_user_bp.route('/', methods=['GET'])
def get_app_users():
    return AppUserController.get_all_app_users()

@app_user_bp.route('/<int:user_id>', methods=['GET'])
def get_app_user(user_id):
    return AppUserController.get_app_user_by_id(user_id)

@app_user_bp.route('/', methods=['POST'])
def create_app_user():
    return AppUserController.create_app_user(request.get_json())

@app_user_bp.route('/<int:user_id>', methods=['PUT'])
def update_app_user(user_id):
    return AppUserController.update_app_user(user_id, request.get_json())

@app_user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_app_user(user_id):
    return AppUserController.delete_app_user(user_id)
