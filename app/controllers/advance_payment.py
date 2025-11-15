# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.advance_payment import AdvancePayment
from ..models.base import db
from ..schemas.advance_payment import AdvancePaymentSchema, AdvancePaymentUpdateSchema

class AdvancePaymentController:
    
    @staticmethod
    def get_all_advance_payments():
        """Obtiene todos los anticipos"""
        try:
            advance_payments = AdvancePayment.query.all()
            return jsonify([ap.to_dict() for ap in advance_payments]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener anticipos', 'details': str(e)}), 500

    @staticmethod
    def get_advance_payment_by_id(advance_payment_id):
        """Obtiene un anticipo por ID"""
        try:
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            return jsonify(advance_payment.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Anticipo no encontrado'}), 404

    @staticmethod
    def create_advance_payment(data):
        """Crea un nuevo anticipo"""
        try:
            schema = AdvancePaymentSchema()
            validated_data = schema.load(data)
            
            advance_payment = AdvancePayment(**validated_data)
            db.session.add(advance_payment)
            db.session.commit()
            
            return jsonify({
                'message': 'Anticipo creado exitosamente',
                'advance_payment': advance_payment.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear anticipo', 'details': str(e)}), 500

    @staticmethod
    def update_advance_payment(advance_payment_id, data):
        """Actualiza un anticipo existente"""
        try:
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            
            schema = AdvancePaymentUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(advance_payment, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Anticipo actualizado exitosamente',
                'advance_payment': advance_payment.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar anticipo', 'details': str(e)}), 500

    @staticmethod
    def delete_advance_payment(advance_payment_id):
        """Elimina un anticipo"""
        try:
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            db.session.delete(advance_payment)
            db.session.commit()
            
            return jsonify({'message': 'Anticipo eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar anticipo', 'details': str(e)}), 500
