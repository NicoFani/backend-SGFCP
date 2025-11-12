# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.expense import Expense
from ..models.base import db
from ..schemas.expense import ExpenseSchema, ExpenseUpdateSchema

class ExpenseController:
    
    @staticmethod
    def get_all_expenses():
        """Obtiene todos los gastos"""
        try:
            expenses = Expense.query.all()
            return jsonify([expense.to_dict() for expense in expenses]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener gastos', 'details': str(e)}), 500

    @staticmethod
    def get_expense_by_id(expense_id):
        """Obtiene un gasto por ID"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            return jsonify(expense.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Gasto no encontrado'}), 404

    @staticmethod
    def create_expense(data):
        """Crea un nuevo gasto"""
        try:
            # Validar datos
            schema = ExpenseSchema()
            validated_data = schema.load(data)
            
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
    def update_expense(expense_id, data):
        """Actualiza un gasto existente"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            
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