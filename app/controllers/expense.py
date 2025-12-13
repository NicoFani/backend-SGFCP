# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.expense import Expense
from ..models.base import db
from ..schemas.expense import ExpenseSchema, ExpenseUpdateSchema

class ExpenseController:
    
    @staticmethod
    def get_all_expenses(current_user_id=None, is_admin=False):
        """Obtiene todos los gastos (filtrados por conductor si no es admin)"""
        try:
            if is_admin:
                expenses = Expense.query.all()
            else:
                # Conductores: ver solo sus propios gastos
                expenses = Expense.query.filter_by(driver_id=current_user_id).all()
            return jsonify([expense.to_dict() for expense in expenses]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener gastos', 'details': str(e)}), 500

    @staticmethod
    def get_expense_by_id(expense_id, current_user_id=None, is_admin=False):
        """Obtiene un gasto por ID (con validación de permisos)"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            
            # Verificar permisos: solo admin o el propio conductor
            if not is_admin and expense.driver_id != current_user_id:
                return jsonify({'error': 'No tienes permisos para ver este gasto'}), 403
            
            return jsonify(expense.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Gasto no encontrado'}), 404

    @staticmethod
    def create_expense(data, current_user_id=None, is_admin=False):
        """Crea un nuevo gasto (admin puede crear cualquiera; chofer puede crear los suyos mientras el viaje esté en curso si se asocia a un viaje)"""
        try:
            # Validar datos
            schema = ExpenseSchema()
            validated_data = schema.load(data)
            
            # Si es chofer, asegurar que driver_id coincide y (si hay trip) que el viaje esté asignado al chofer y en curso
            if not is_admin:
                if validated_data.get('driver_id') != current_user_id:
                    return jsonify({'error': 'No puedes crear gastos para otro chofer'}), 403
                trip_id = validated_data.get('trip_id')
                if trip_id is not None:
                    from ..models.trip import Trip
                    trip = Trip.query.get(trip_id)
                    if not trip:
                        return jsonify({'error': 'Viaje no encontrado'}), 404
                    # Validar que el chofer esté asignado al viaje (relación muchos-a-muchos) y que esté en curso
                    if not any(d.id == current_user_id for d in trip.drivers):
                        return jsonify({'error': 'No puedes crear gastos para viajes no asignados a ti'}), 403
                    if trip.state_id != 'En curso':
                        return jsonify({'error': 'Solo puedes cargar gastos cuando el viaje está en curso'}), 403
            
            # Crear gasto
            expense = Expense(**validated_data)
            db.session.add(expense)
            db.session.commit()
            
            return jsonify({
                'message': 'Gasto creado exitosamente',
                'expense': expense.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear gasto', 'details': str(e)}), 500

    @staticmethod
    def update_expense(expense_id, data, current_user_id=None, is_admin=False):
        """Actualiza un gasto existente (solo admin puede editar)"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            
            # Chofer no puede editar
            if not is_admin:
                return jsonify({'error': 'No tienes permisos para editar gastos'}), 403
            
            # Validar datos
            schema = ExpenseUpdateSchema()
            validated_data = schema.load(data)
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(expense, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Gasto actualizado exitosamente',
                'expense': expense.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar gasto', 'details': str(e)}), 500

    @staticmethod
    def delete_expense(expense_id):
        """Elimina un gasto"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            db.session.delete(expense)
            db.session.commit()
            
            return jsonify({'message': 'Gasto eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar gasto', 'details': str(e)}), 500

    @staticmethod
    def get_expenses_by_trip(trip_id):
        """Obtiene todos los gastos de un viaje especifico"""
        try:
            expenses = Expense.query.filter_by(trip_id=trip_id).all()
            return jsonify([expense.to_dict() for expense in expenses]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener gastos del viaje', 'details': str(e)}), 500

    @staticmethod
    def get_expenses_by_type(expense_type):
        """Obtiene gastos filtrados por tipo"""
        try:
            expenses = Expense.query.filter_by(expense_type=expense_type).all()
            return jsonify([expense.to_dict() for expense in expenses]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener gastos por tipo', 'details': str(e)}), 500