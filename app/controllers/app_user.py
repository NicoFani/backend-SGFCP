# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token
from ..models.app_user import AppUser
from ..models.base import db
from ..schemas.app_user import AppUserSchema, AppUserUpdateSchema, LoginSchema, RegisterSchema
from .. import bcrypt

class AppUserController:
    
    @staticmethod
    def get_all_app_users():
        """Obtiene todos los usuarios"""
        try:
            users = AppUser.query.all()
            return jsonify([user.to_dict() for user in users]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener usuarios', 'details': str(e)}), 500

    @staticmethod
    def get_app_user_by_id(user_id):
        """Obtiene un usuario por ID"""
        try:
            user = AppUser.query.get_or_404(user_id)
            return jsonify(user.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Usuario no encontrado'}), 404

    @staticmethod
    def create_app_user(data):
        """Crea un nuevo usuario"""
        try:
            schema = AppUserSchema()
            validated_data = schema.load(data)
            
            # Hash password
            password = validated_data.pop('password')
            validated_data['password_hash'] = bcrypt.generate_password_hash(password).decode('utf-8')
            
            user = AppUser(**validated_data)
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'Usuario creado exitosamente',
                'user': user.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear usuario', 'details': str(e)}), 500
    
    @staticmethod
    def register_user(data):
        """Registra un nuevo usuario"""
        try:
            schema = RegisterSchema()
            validated_data = schema.load(data)
            
            # Verificar si el email ya existe
            existing_user = AppUser.query.filter_by(email=validated_data['email']).first()
            if existing_user:
                return jsonify({'error': 'El email ya está registrado'}), 409
            
            # Hash password
            password = validated_data.pop('password')
            validated_data['password_hash'] = bcrypt.generate_password_hash(password).decode('utf-8')
            
            user = AppUser(**validated_data)
            db.session.add(user)
            db.session.commit()
            
            # Generar tokens JWT
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'message': 'Usuario registrado exitosamente',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al registrar usuario', 'details': str(e)}), 500
    
    @staticmethod
    def login_user(data):
        """Autentica un usuario y devuelve JWT tokens"""
        try:
            schema = LoginSchema()
            validated_data = schema.load(data)
            
            # Buscar usuario por email
            user = AppUser.query.filter_by(email=validated_data['email']).first()
            
            if not user:
                return jsonify({'error': 'Credenciales inválidas'}), 401
            
            # Verificar contraseña
            if not bcrypt.check_password_hash(user.password_hash, validated_data['password']):
                return jsonify({'error': 'Credenciales inválidas'}), 401
            
            # Verificar que el usuario esté activo
            if not user.is_active:
                return jsonify({'error': 'Usuario inactivo'}), 403
            
            # Generar tokens JWT
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'message': 'Login exitoso',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except Exception as e:
            return jsonify({'error': 'Error al procesar login', 'details': str(e)}), 500

    @staticmethod
    def update_app_user(user_id, data):
        """Actualiza un usuario existente"""
        try:
            user = AppUser.query.get_or_404(user_id)
            
            schema = AppUserUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(user, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Usuario actualizado exitosamente',
                'user': user.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar usuario', 'details': str(e)}), 500

    @staticmethod
    def delete_app_user(user_id):
        """Elimina un usuario"""
        try:
            user = AppUser.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar usuario', 'details': str(e)}), 500
