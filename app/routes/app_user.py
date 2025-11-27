from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers.app_user import AppUserController
from ..utils import admin_required

app_user_bp = Blueprint('app_user', __name__, url_prefix='/users')

# GET all users (solo admin)
@app_user_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required()
def get_app_users():
    return AppUserController.get_all_app_users()

# GET one user (solo el propio usuario o admin)
@app_user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_app_user(user_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    if not is_admin and current_user_id != user_id:
        return {'error': 'No tienes permisos para ver este usuario'}, 403
    
    return AppUserController.get_app_user_by_id(user_id)

# CREATE user (solo admin)
@app_user_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_app_user():
    return AppUserController.create_app_user(request.get_json())

# UPDATE user (solo el propio usuario o admin)
@app_user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_app_user(user_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    if not is_admin and current_user_id != user_id:
        return {'error': 'No tienes permisos para actualizar este usuario'}, 403
    
    return AppUserController.update_app_user(user_id, request.get_json())

# DELETE user (solo admin)
@app_user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_app_user(user_id):
    return AppUserController.delete_app_user(user_id)
