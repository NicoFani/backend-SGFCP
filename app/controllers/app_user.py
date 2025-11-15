# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.app_user import AppUser
from ..models.base import db
from ..schemas.app_user import AppUserSchema, AppUserUpdateSchema

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
