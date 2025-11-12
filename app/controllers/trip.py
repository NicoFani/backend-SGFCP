# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.trip import Trip
from ..models.base import db
from ..schemas.trip import TripSchema, TripUpdateSchema

class TripController:
    
    @staticmethod
    def get_all_trips():
        """Obtiene todos los viajes"""
        try:
            trips = Trip.query.all()
            return jsonify([trip.to_dict() for trip in trips]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener viajes', 'details': str(e)}), 500

    @staticmethod
    def get_trip_by_id(trip_id):
        """Obtiene un viaje por ID"""
        try:
            trip = Trip.query.get_or_404(trip_id)
            return jsonify(trip.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Viaje no encontrado'}), 404

    @staticmethod
    def create_trip(data):
        """Crea un nuevo viaje"""
        try:
            # Validar datos
            schema = TripSchema()
            validated_data = schema.load(data)
            
            # Crear viaje
            trip = Trip(**validated_data)
            db.session.add(trip)
            db.session.commit()
            
            return jsonify({
                'message': 'Viaje creado exitosamente',
                'trip': trip.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear viaje', 'details': str(e)}), 500

    @staticmethod
    def update_trip(trip_id, data):
        """Actualiza un viaje existente"""
        try:
            trip = Trip.query.get_or_404(trip_id)
            
            # Validar datos
            schema = TripUpdateSchema()
            validated_data = schema.load(data)
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(trip, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Viaje actualizado exitosamente',
                'trip': trip.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar viaje', 'details': str(e)}), 500

    @staticmethod
    def delete_trip(trip_id):
        """Elimina un viaje"""
        try:
            trip = Trip.query.get_or_404(trip_id)
            db.session.delete(trip)
            db.session.commit()
            
            return jsonify({'message': 'Viaje eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar viaje', 'details': str(e)}), 500

    @staticmethod
    def get_trips_by_driver(driver_id):
        """Obtiene todos los viajes de un conductor especifico"""
        try:
            trips = Trip.query.filter_by(driver_id=driver_id).all()
            return jsonify([trip.to_dict() for trip in trips]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener viajes del conductor', 'details': str(e)}), 500

    @staticmethod
    def get_trips_by_state(state):
        """Obtiene viajes filtrados por estado"""
        try:
            trips = Trip.query.filter_by(state_id=state).all()
            return jsonify([trip.to_dict() for trip in trips]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener viajes por estado', 'details': str(e)}), 500