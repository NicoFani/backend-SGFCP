# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.load_owner import LoadOwner
from ..models.base import db
from ..schemas.load_owner import LoadOwnerSchema, LoadOwnerUpdateSchema

class LoadOwnerController:
    
    @staticmethod
    def get_all_load_owners():
        """Obtiene todos los dueños de carga"""
        try:
            load_owners = LoadOwner.query.all()
            return jsonify([lo.to_dict() for lo in load_owners]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener dueños de carga', 'details': str(e)}), 500

    @staticmethod
    def get_load_owner_by_id(load_owner_id):
        """Obtiene un dueño de carga por ID"""
        try:
            load_owner = LoadOwner.query.get_or_404(load_owner_id)
            return jsonify(load_owner.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Dueño de carga no encontrado'}), 404

    @staticmethod
    def create_load_owner(data):
        """Crea un nuevo dueño de carga"""
        try:
            schema = LoadOwnerSchema()
            validated_data = schema.load(data)
            
            load_owner = LoadOwner(**validated_data)
            db.session.add(load_owner)
            db.session.commit()
            
            return jsonify({
                'message': 'Dueño de carga creado exitosamente',
                'load_owner': load_owner.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear dueño de carga', 'details': str(e)}), 500

    @staticmethod
    def update_load_owner(load_owner_id, data):
        """Actualiza un dueño de carga existente"""
        try:
            load_owner = LoadOwner.query.get_or_404(load_owner_id)
            
            schema = LoadOwnerUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(load_owner, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Dueño de carga actualizado exitosamente',
                'load_owner': load_owner.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar dueño de carga', 'details': str(e)}), 500

    @staticmethod
    def delete_load_owner(load_owner_id):
        """Elimina un dueño de carga"""
        try:
            from ..models.trip import Trip
            
            load_owner = LoadOwner.query.get_or_404(load_owner_id)
            
            # Verificar si tiene viajes activos (no finalizados)
            active_trips = Trip.query.filter(
                Trip.load_owner_id == load_owner_id,
                Trip.state_id != 'Finalizado'
            ).count()
            
            if active_trips > 0:
                return jsonify({
                    'error': 'No se puede eliminar el dador porque tiene viajes activos',
                    'details': f'Hay {active_trips} viaje(s) que no están finalizados'
                }), 400
            
            db.session.delete(load_owner)
            db.session.commit()
            
            return jsonify({'message': 'Dueño de carga eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar dueño de carga', 'details': str(e)}), 500
            db.session.rollback()
            return jsonify({'error': 'Error al convertir dador', 'details': str(e)}), 500
