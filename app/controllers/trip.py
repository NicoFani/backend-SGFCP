# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.trip import Trip
from ..models.driver import Driver
from ..models.base import db
from ..schemas.trip import TripSchema, TripUpdateSchema

class TripController:
    
    @staticmethod
    def get_all_trips(current_user_id=None, is_admin=False):
        """Obtiene todos los viajes (filtrados por conductor si no es admin)"""
        try:
            if is_admin:
                trips = Trip.query.all()
            else:
                # Los conductores solo ven sus propios viajes
                trips = Trip.query.filter(Trip.driver_id == current_user_id).all()
            return jsonify([trip.to_dict() for trip in trips]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener viajes', 'details': str(e)}), 500

    @staticmethod
    def get_trip_by_id(trip_id, current_user_id=None, is_admin=False):
        """Obtiene un viaje por ID (con validación de permisos)"""
        try:
            trip = Trip.query.get_or_404(trip_id)
            
            # Verificar permisos: solo admin o el conductor asignado al viaje
            if not is_admin:
                if current_user_id != trip.driver_id:
                    return jsonify({'error': 'No tienes permisos para ver este viaje'}), 403
            
            return jsonify(trip.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Viaje no encontrado'}), 404

    @staticmethod
    def create_trip(data):
        """Crea uno o múltiples viajes (uno por cada chofer seleccionado)"""
        try:
            # Extraer lista de drivers (puede venir como 'drivers' o 'driver_id')
            drivers_ids = data.pop('drivers', None)
            if drivers_ids is None:
                # Si viene driver_id, convertir a lista
                driver_id = data.get('driver_id')
                drivers_ids = [driver_id] if driver_id else []
            
            if not drivers_ids:
                return jsonify({'error': 'Debe especificar al menos un chofer'}), 400
            
            # Verificar que los drivers existan
            drivers = Driver.query.filter(Driver.id.in_(drivers_ids)).all()
            if len(drivers) != len(drivers_ids):
                return jsonify({'error': 'Uno o más choferes no existen'}), 400
            
            created_trips = []
            schema = TripSchema()
            
            # Crear un viaje por cada chofer
            for driver in drivers:
                trip_data = data.copy()
                trip_data['driver_id'] = driver.id
                
                # Validar DESPUÉS de asignar driver_id
                validated_data = schema.load(trip_data)
                trip = Trip(**validated_data)
                
                db.session.add(trip)
                created_trips.append(trip)
            
            db.session.commit()
            
            return jsonify({
                'message': f'{len(created_trips)} viaje(s) creado(s) exitosamente',
                'trips': [trip.to_dict() for trip in created_trips]
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear viaje', 'details': str(e)}), 500

    @staticmethod
    def update_trip(trip_id, data, current_user_id=None, is_admin=False):
        """Actualiza un viaje existente (admin puede todo, chofer solo ciertos campos)"""
        try:
            trip = Trip.query.get_or_404(trip_id)
            
            # Verificar permisos: solo admin o el conductor asignado al viaje
            if not is_admin:
                if current_user_id != trip.driver_id:
                    return jsonify({'error': 'No tienes permisos para actualizar este viaje'}), 403
            
            # Validar datos
            # Pasar el peso de carga actual como contexto para validar el peso de descarga
            schema = TripUpdateSchema()
            schema.context = {'load_weight_on_load': trip.load_weight_on_load}
            validated_data = schema.load(data)
            
            # Si es chofer, solo puede actualizar ciertos campos según el estado
            if not is_admin:
                if trip.state_id == 'Pendiente':
                    # Verificar si el chofer está intentando iniciar el viaje (cambio a "En curso")
                    if 'state_id' in validated_data and validated_data['state_id'] == 'En curso':
                        # Verificar que el chofer no tenga otro viaje en curso
                        existing_trip = Trip.query.filter(
                            Trip.driver_id == trip.driver_id,
                            Trip.state_id == 'En curso',
                            Trip.id != trip_id
                        ).first()
                        
                        if existing_trip:
                            return jsonify({
                                'error': 'No puedes iniciar un nuevo viaje mientras tienes un viaje en curso',
                                'details': f'Tienes el viaje #{existing_trip.id} en curso'
                            }), 400
                    
                    # Chofer iniciando viaje: puede cargar datos de inicio
                    allowed_fields = [
                        'document_type',            # Tipo de documento (CTG/Remito)
                        'document_number',          # Número de documento
                        'estimated_kms',            # Kms a recorrer
                        'load_weight_on_load',      # Peso de carga estimado
                        'load_owner_id',            # Dador de carga
                        'fuel_on_client',           # Vale de combustible
                        'fuel_liters',              # Litros del vale
                        'state_id',                 # Estado (Pendiente -> En curso)
                        'load_type_id',             # Tipo de carga
                        'calculated_per_km',        # Cálculo por km o por viaje
                        'rate',                     # Tarifa del viaje
                    ]
                elif trip.state_id == 'En curso':
                    # Chofer finalizando viaje: puede cargar datos de fin
                    allowed_fields = [
                        'end_date',                 # Fecha fin
                        'load_weight_on_unload',    # Peso de descarga
                        'state_id',                 # Estado (En curso -> Finalizado)
                    ]
                else:
                    # Estado Finalizado: chofer no puede editar
                    allowed_fields = []
                
                # Filtrar solo campos permitidos
                filtered_data = {k: v for k, v in validated_data.items() if k in allowed_fields}
                
                # Validar transiciones de estado
                if 'state_id' in filtered_data:
                    current_state = trip.state_id
                    new_state = filtered_data['state_id']
                    
                    # Validar transiciones permitidas
                    valid_transitions = [
                        ('Pendiente', 'En curso'),
                        ('En curso', 'Finalizado')
                    ]
                    
                    if (current_state, new_state) not in valid_transitions:
                        return jsonify({'error': f'Transición de estado no permitida: {current_state} -> {new_state}'}), 403
                
                validated_data = filtered_data
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(trip, field, value)
            
            db.session.commit()
            
            # Si el viaje se acaba de finalizar, verificar si necesita ajuste retroactivo
            # y recalcular resúmenes en "calculation_pending"
            if 'state_id' in validated_data and validated_data['state_id'] == 'Finalizado':
                try:
                    from app.controllers.payroll_adjustment import PayrollAdjustmentController
                    PayrollAdjustmentController.auto_create_trip_adjustment(trip)
                except Exception as e:
                    # No fallar la actualización del viaje si hay error en el ajuste
                    print(f"Error creando ajuste automático para viaje {trip.id}: {str(e)}")
                
                # Recalcular resúmenes en "calculation_pending" para este chofer
                try:
                    from app.scheduler import recalculate_pending_payroll_summaries
                    from ..models.payroll_period import PayrollPeriod
                    
                    # Encontrar el período que contiene este viaje
                    period = PayrollPeriod.query.filter(
                        PayrollPeriod.start_date <= trip.start_date,
                        PayrollPeriod.end_date >= trip.start_date
                    ).first()
                    
                    if period:
                        recalculate_pending_payroll_summaries(trip.driver_id, period.id)
                except Exception as e:
                    print(f"Error recalculando resúmenes automáticos para viaje {trip.id}: {str(e)}")
            
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
        """Elimina un viaje (solo admin)"""
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
            trips = Trip.query.filter(Trip.driver_id == driver_id).all()
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