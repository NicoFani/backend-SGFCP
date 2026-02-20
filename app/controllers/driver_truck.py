# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.driver_truck import DriverTruck
from ..models.truck import Truck
from ..models.base import db
from ..schemas.driver_truck import DriverTruckSchema, DriverTruckUpdateSchema

class DriverTruckController:
    
    @staticmethod
    def get_all_driver_trucks():
        """Obtiene todas las asignaciones conductor-camión"""
        try:
            driver_trucks = DriverTruck.query.all()
            return jsonify([dt.to_dict() for dt in driver_trucks]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener asignaciones', 'details': str(e)}), 500

    @staticmethod
    def get_trucks_by_driver(driver_id):
        """Obtiene todos los camiones asignados a un conductor (histórico)"""
        try:
            # Obtener todas las asignaciones del conductor, ordenadas por fecha descendente
            assignments = DriverTruck.query.filter_by(driver_id=driver_id).order_by(DriverTruck.date.desc()).all()
            
            # Obtener los IDs únicos de camiones (manteniendo el orden)
            truck_ids_seen = set()
            truck_ids = []
            for assignment in assignments:
                if assignment.truck_id not in truck_ids_seen:
                    truck_ids.append(assignment.truck_id)
                    truck_ids_seen.add(assignment.truck_id)
            
            # Obtener los detalles de los camiones
            trucks = []
            for truck_id in truck_ids:
                truck = Truck.query.get(truck_id)
                if truck:
                    trucks.append(truck.to_dict())
            
            return jsonify(trucks), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener camiones del conductor', 'details': str(e)}), 500

    @staticmethod
    def get_current_truck_by_driver(driver_id):
        """Obtiene el camión actual de un conductor (el más reciente por fecha)"""
        try:
            # Obtener la asignación más reciente del conductor
            assignment = DriverTruck.query.filter_by(driver_id=driver_id).order_by(DriverTruck.date.desc()).first()
            
            if not assignment:
                return None
            
            # Obtener el camión
            truck = Truck.query.get(assignment.truck_id)
            if truck:
                return truck.to_dict()
            
            return None
        except SQLAlchemyError:
            return None

    @staticmethod
    def get_current_assignment_by_truck(truck_id):
        """Obtiene la asignación actual de un camión (la más reciente por fecha)"""
        try:
            assignment = DriverTruck.query.filter_by(truck_id=truck_id).order_by(DriverTruck.date.desc()).first()

            if not assignment:
                return None

            return assignment.to_dict()
        except SQLAlchemyError:
            return None

    @staticmethod
    def get_driver_truck_by_id(driver_truck_id):
        """Obtiene una asignación por ID"""
        try:
            driver_truck = DriverTruck.query.get_or_404(driver_truck_id)
            return jsonify(driver_truck.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Asignación no encontrada'}), 404

    @staticmethod
    def create_driver_truck(data):
        """Crea una nueva asignación conductor-camión"""
        try:
            schema = DriverTruckSchema()
            validated_data = schema.load(data)
            
            driver_truck = DriverTruck(**validated_data)
            db.session.add(driver_truck)
            db.session.commit()
            
            return jsonify({
                'message': 'Asignación creada exitosamente',
                'driver_truck': driver_truck.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear asignación', 'details': str(e)}), 500

    @staticmethod
    def update_driver_truck(driver_truck_id, data):
        """Actualiza una asignación existente"""
        try:
            driver_truck = DriverTruck.query.get_or_404(driver_truck_id)
            
            schema = DriverTruckUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(driver_truck, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Asignación actualizada exitosamente',
                'driver_truck': driver_truck.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar asignación', 'details': str(e)}), 500

    @staticmethod
    def delete_driver_truck(driver_truck_id):
        """Elimina una asignación"""
        try:
            driver_truck = DriverTruck.query.get_or_404(driver_truck_id)
            db.session.delete(driver_truck)
            db.session.commit()
            
            return jsonify({'message': 'Asignación eliminada exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar asignación', 'details': str(e)}), 500
