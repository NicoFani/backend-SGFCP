# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.truck import Truck
from ..models.base import db
from ..schemas.truck import TruckSchema, TruckUpdateSchema

class TruckController:
    
    @staticmethod
    def get_all_trucks():
        """Obtiene todos los camiones"""
        try:
            trucks = Truck.query.all()
            return jsonify([truck.to_dict() for truck in trucks]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener camiones', 'details': str(e)}), 500

    @staticmethod
    def get_truck_by_id(truck_id):
        """Obtiene un camion por ID"""
        try:
            truck = Truck.query.get_or_404(truck_id)
            return jsonify(truck.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Camión no encontrado'}), 404

    @staticmethod
    def create_truck(data):
        """Crea un nuevo camion"""
        try:
            # Validar datos
            schema = TruckSchema()
            validated_data = schema.load(data)
            
            # Crear camion
            truck = Truck(**validated_data)
            db.session.add(truck)
            db.session.commit()
            
            return jsonify({
                'message': 'Camion creado exitosamente',
                'truck': truck.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear camion', 'details': str(e)}), 500

    @staticmethod
    def update_truck(truck_id, data):
        """Actualiza un camion existente"""
        try:
            truck = Truck.query.get_or_404(truck_id)
            
            # Validar datos
            schema = TruckUpdateSchema()
            validated_data = schema.load(data)
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(truck, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Camion actualizado exitosamente',
                'truck': truck.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar camion', 'details': str(e)}), 500

    @staticmethod
    def delete_truck(truck_id):
        """Elimina un camion"""
        try:
            truck = Truck.query.get_or_404(truck_id)
            db.session.delete(truck)
            db.session.commit()
            
            return jsonify({'message': 'Camion eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar camion', 'details': str(e)}), 500

    @staticmethod
    def get_truck_current_driver(truck_id):
        """Obtiene el chofer actual asignado a un camion"""
        try:
            from ..models.driver_truck import DriverTruck
            from ..models.driver import Driver
            
            truck = Truck.query.get_or_404(truck_id)
            
            # Obtener la asignación más reciente
            driver_truck = DriverTruck.query.filter_by(truck_id=truck_id)\
                .order_by(DriverTruck.date.desc())\
                .first()
            
            if not driver_truck:
                return jsonify({'driver': None}), 200
            
            # Obtener el conductor
            driver = Driver.query.get(driver_truck.driver_id)
            
            if not driver:
                return jsonify({'driver': None}), 200
            
            return jsonify({
                'driver': driver.to_dict(),
                'assignment_date': driver_truck.date.isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Error al obtener chofer del camión', 'details': str(e)}), 500