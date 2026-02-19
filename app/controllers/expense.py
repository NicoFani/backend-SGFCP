# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.expense import Expense
from ..models.payroll_detail import PayrollDetail
from ..models.base import db
from ..schemas.expense import ExpenseSchema, ExpenseUpdateSchema
from ..models.payroll_period import PayrollPeriod
from ..models.payroll_summary import PayrollSummary

class ExpenseController:

    @staticmethod
    def _is_period_locked_for_driver(driver_id, expense_date):
        """True si el período de la fecha tiene resumen aprobado para ese chofer."""
        if not driver_id or not expense_date:
            return False

        period = PayrollPeriod.query.filter(
            PayrollPeriod.start_date <= expense_date,
            PayrollPeriod.end_date >= expense_date
        ).first()

        if not period:
            return False

        approved_summary = PayrollSummary.query.filter_by(
            period_id=period.id,
            driver_id=driver_id,
            status='approved'
        ).first()

        return approved_summary is not None

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
        """Crea un nuevo gasto (admin puede crear cualquiera; chofer puede crear los suyos si el viaje está asignado a él)."""
        try:
            # Validar datos
            schema = ExpenseSchema()
            validated_data = schema.load(data)

            # Si hay viaje asociado, forzar consistencia chofer-gasto con el chofer del viaje
            trip = None
            trip_id = validated_data.get('trip_id')
            if trip_id is not None:
                from ..models.trip import Trip
                trip = Trip.query.get(trip_id)
                if not trip:
                    return jsonify({'error': 'Viaje no encontrado'}), 404
                validated_data['driver_id'] = trip.driver_id
            
            # Si es chofer, asegurar que driver_id coincide y (si hay trip) que el viaje esté asignado al chofer
            if not is_admin:
                if validated_data.get('driver_id') != current_user_id:
                    return jsonify({'error': 'No puedes crear gastos para otro chofer'}), 403
                if trip is not None:
                    # Validar que el chofer esté asignado al viaje (relación uno-a-uno) y que esté en curso
                    if trip.driver_id != current_user_id:
                        return jsonify({'error': 'No puedes crear gastos para viajes no asignados a ti'}), 403

            # Bloqueo por período aprobado (único bloqueo funcional)
            if ExpenseController._is_period_locked_for_driver(
                validated_data.get('driver_id'),
                validated_data.get('date')
            ):
                return jsonify({
                    'error': 'No puedes modificar gastos: el período del chofer está aprobado'
                }), 403
            
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
        """Actualiza un gasto existente (admin o el propio chofer)"""
        try:
            expense = Expense.query.get_or_404(expense_id)
            
            # Chofer solo puede editar sus propios gastos
            if not is_admin:
                if expense.driver_id != current_user_id:
                    return jsonify({'error': 'No tienes permisos para editar este gasto'}), 403
            
            # Validar datos
            schema = ExpenseUpdateSchema()
            validated_data = schema.load(data)

            # Si hay viaje asociado (nuevo o existente), forzar consistencia chofer-gasto con chofer del viaje
            effective_trip_id = validated_data.get('trip_id', expense.trip_id)
            if effective_trip_id is not None:
                from ..models.trip import Trip
                trip = Trip.query.get(effective_trip_id)
                if not trip:
                    return jsonify({'error': 'Viaje no encontrado'}), 404
                validated_data['driver_id'] = trip.driver_id

            old_driver_id = expense.driver_id
            old_date = expense.date
            new_driver_id = validated_data.get('driver_id', old_driver_id)
            new_date = validated_data.get('date', old_date)

            # Bloqueo por período aprobado (estado actual o nuevo)
            if ExpenseController._is_period_locked_for_driver(old_driver_id, old_date):
                return jsonify({
                    'error': 'No puedes modificar este gasto: el período del chofer está aprobado'
                }), 403

            if (new_driver_id != old_driver_id or new_date != old_date) and \
                ExpenseController._is_period_locked_for_driver(new_driver_id, new_date):
                return jsonify({
                    'error': 'No puedes mover este gasto: el período destino del chofer está aprobado'
                }), 403
            
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

            # Bloqueo por período aprobado
            if ExpenseController._is_period_locked_for_driver(expense.driver_id, expense.date):
                return jsonify({
                    'error': 'No puedes eliminar este gasto: el período del chofer está aprobado'
                }), 403

            # Limpiar referencias históricas para evitar errores de FK
            PayrollDetail.query.filter_by(expense_id=expense.id).update(
                {'expense_id': None},
                synchronize_session=False
            )

            Expense.query.filter_by(id=expense.id).delete(synchronize_session=False)
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