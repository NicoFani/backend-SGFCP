# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.driver import Driver
from ..models.base import db
from ..schemas.driver import DriverSchema, DriverUpdateSchema

class DriverController:
    
    @staticmethod
    def get_all_drivers(current_user_id=None, is_admin=False):
        """Obtiene todos los conductores (solo admin puede ver todos)"""
        try:
            if is_admin:
                drivers = Driver.query.all()
            else:
                # Los conductores solo pueden ver su propia información
                drivers = Driver.query.filter_by(id=current_user_id).all()
            return jsonify([driver.to_dict() for driver in drivers]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener conductores', 'details': str(e)}), 500

    @staticmethod
    def get_driver_by_id(driver_id):
        """Obtiene un conductor por ID"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            return jsonify(driver.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Conductor no encontrado'}), 404

    @staticmethod
    def create_driver(data):
        """Crea un nuevo conductor"""
        try:
            # Validar datos
            schema = DriverSchema()
            validated_data = schema.load(data)
            
            # Crear conductor
            driver = Driver(**validated_data)
            db.session.add(driver)
            db.session.commit()
            
            return jsonify({
                'message': 'Conductor creado exitosamente',
                'driver': driver.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear conductor', 'details': str(e)}), 500

    @staticmethod
    def update_driver(driver_id, data):
        """Actualiza un conductor existente"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            
            # Validar datos
            schema = DriverUpdateSchema()
            validated_data = schema.load(data)
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(driver, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Conductor actualizado exitosamente',
                'driver': driver.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar conductor', 'details': str(e)}), 500

    @staticmethod
    def delete_driver(driver_id):
        """Elimina un conductor"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            db.session.delete(driver)
            db.session.commit()
            
            return jsonify({'message': 'Conductor eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar conductor', 'details': str(e)}), 500