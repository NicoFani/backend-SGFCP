# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.advance_payment import AdvancePayment
from ..models.base import db
from ..schemas.advance_payment import AdvancePaymentSchema, AdvancePaymentUpdateSchema

class AdvancePaymentController:
    
    @staticmethod
    def get_all_advance_payments(current_user_id=None, is_admin=False):
        """Obtiene todos los anticipos (solo admin puede ver todos)"""
        try:
            if is_admin:
                advance_payments = AdvancePayment.query.all()
            else:
                # Los choferes solo pueden ver sus propios adelantos
                advance_payments = AdvancePayment.query.filter_by(driver_id=current_user_id).all()
            return jsonify([ap.to_dict() for ap in advance_payments]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener anticipos', 'details': str(e)}), 500

    @staticmethod
    def get_advance_payment_by_id(advance_payment_id, current_user_id=None, is_admin=False):
        """Obtiene un anticipo por ID (con validación de permisos)"""
        try:
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            
            # Verificar permisos: solo admin o el propio chofer
            if not is_admin and advance_payment.driver_id != current_user_id:
                return jsonify({'error': 'No tienes permisos para ver este anticipo'}), 403
            
            return jsonify(advance_payment.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Anticipo no encontrado'}), 404

    @staticmethod
    def create_advance_payment(data, current_user_id=None, is_admin=False):
        """Crea un nuevo anticipo (solo admin puede crear)"""
        try:
            if not is_admin:
                return jsonify({'error': 'Solo los administradores pueden crear anticipos'}), 403
            
            schema = AdvancePaymentSchema()
            validated_data = schema.load(data)
            
            # Establecer el admin_id del usuario autenticado
            validated_data['admin_id'] = current_user_id
            
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
    def update_advance_payment(advance_payment_id, data, current_user_id=None, is_admin=False):
        """Actualiza un anticipo existente (solo admin puede actualizar)"""
        try:
            if not is_admin:
                return jsonify({'error': 'Solo los administradores pueden actualizar anticipos'}), 403
            
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            
            schema = AdvancePaymentUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                # No permitir cambiar el admin_id
                if field != 'admin_id':
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
    def delete_advance_payment(advance_payment_id, current_user_id=None, is_admin=False):
        """Elimina un anticipo (solo admin puede eliminar)"""
        try:
            if not is_admin:
                return jsonify({'error': 'Solo los administradores pueden eliminar anticipos'}), 403
            
            advance_payment = AdvancePayment.query.get_or_404(advance_payment_id)
            db.session.delete(advance_payment)
            db.session.commit()
            
            return jsonify({'message': 'Anticipo eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar anticipo', 'details': str(e)}), 500
