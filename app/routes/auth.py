from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app import bcrypt
from app.models.app_user import AppUser
from app.db import db
from marshmallow import Schema, fields, validate, ValidationError
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# Schemas de validación
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    surname = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    is_admin = fields.Boolean(required=False, load_default=False)

login_schema = LoginSchema()
register_schema = RegisterSchema()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login que devuelve access y refresh tokens"""
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    user = AppUser.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Usuario inactivo'}), 403
    
    # Verificar contraseña
    if not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401
    
    # Crear tokens con información adicional
    additional_claims = {
        'is_admin': user.is_admin,
        'name': user.name,
        'surname': user.surname
    }
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict_safe()
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro de nuevos usuarios (solo admin puede crear otros admins)"""
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Datos inválidos', 'details': err.messages}), 400
    
    # Verificar si el email ya existe
    if AppUser.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 409
    
    # Hash de la contraseña
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Crear usuario
    new_user = AppUser(
        name=data['name'],
        surname=data['surname'],
        email=data['email'],
        password_hash=password_hash,
        is_admin=data.get('is_admin', False),
        is_active=True
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': new_user.to_dict_safe()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear usuario', 'details': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar el access token usando el refresh token"""
    current_user_id = int(get_jwt_identity())
    user = AppUser.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'Usuario no encontrado o inactivo'}), 404
    
    additional_claims = {
        'is_admin': user.is_admin,
        'name': user.name,
        'surname': user.surname
    }
    
    new_access_token = create_access_token(
        identity=str(current_user_id),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    return jsonify({
        'access_token': new_access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obtener información del usuario actual"""
    current_user_id = int(get_jwt_identity())
    user = AppUser.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(user.to_dict_safe()), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint de logout (el cliente debe eliminar el token)"""
    # Con JWT no necesitamos hacer nada en el servidor
    # El cliente simplemente elimina el token
    return jsonify({'message': 'Logout exitoso'}), 200
