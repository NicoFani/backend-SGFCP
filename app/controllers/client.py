# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.client import Client
from ..models.base import db
from ..schemas.client import ClientSchema, ClientUpdateSchema

class ClientController:
    
    @staticmethod
    def get_all_clients():
        """Obtiene todos los clientes"""
        try:
            clients = Client.query.all()
            return jsonify([client.to_dict() for client in clients]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener clientes', 'details': str(e)}), 500

    @staticmethod
    def get_client_by_id(client_id):
        """Obtiene un cliente por ID"""
        try:
            client = Client.query.get_or_404(client_id)
            return jsonify(client.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Cliente no encontrado'}), 404

    @staticmethod
    def create_client(data):
        """Crea un nuevo cliente"""
        try:
            schema = ClientSchema()
            validated_data = schema.load(data)
            
            client = Client(**validated_data)
            db.session.add(client)
            db.session.commit()
            
            return jsonify({
                'message': 'Cliente creado exitosamente',
                'client': client.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear cliente', 'details': str(e)}), 500

    @staticmethod
    def update_client(client_id, data):
        """Actualiza un cliente existente"""
        try:
            client = Client.query.get_or_404(client_id)
            
            schema = ClientUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(client, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Cliente actualizado exitosamente',
                'client': client.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar cliente', 'details': str(e)}), 500

    @staticmethod
    def delete_client(client_id):
        """Elimina un cliente"""
        try:
            from ..models.trip import Trip
            
            client = Client.query.get_or_404(client_id)
            
            # Verificar si tiene viajes activos (no finalizados)
            active_trips = Trip.query.filter(
                Trip.client_id == client_id,
                Trip.state_id != 'Finalizado'
            ).count()
            
            if active_trips > 0:
                return jsonify({
                    'error': 'No se puede eliminar el cliente porque tiene viajes activos',
                    'details': f'Hay {active_trips} viaje(s) que no están finalizados'
                }), 400
            
            db.session.delete(client)
            db.session.commit()
            
            return jsonify({'message': 'Cliente eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar cliente', 'details': str(e)}), 500
            db.session.rollback()
            return jsonify({'error': 'Error al convertir cliente', 'details': str(e)}), 500
