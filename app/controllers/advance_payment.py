# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.advance_payment import AdvancePayment
from ..models.base import db
from ..schemas.advance_payment import AdvancePaymentSchema, AdvancePaymentUpdateSchema
from ..controllers.notification import NotificationController
from ..utils.supabase_storage import supabase_storage

class AdvancePaymentController:
    
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    @staticmethod
    def _allowed_file(filename):
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in AdvancePaymentController.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_all_advance_payments(current_user_id=None, is_admin=False):
        """Obtiene todos los anticipos (solo admin puede ver todos)"""
        try:
            if is_admin:
                advance_payments = AdvancePayment.query.order_by(AdvancePayment.date.desc()).all()
            else:
                # Los choferes solo pueden ver sus propios adelantos
                advance_payments = AdvancePayment.query.filter_by(driver_id=current_user_id).order_by(AdvancePayment.date.desc()).all()
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
    def get_advance_payments_by_driver(driver_id, current_user_id=None, is_admin=False):
        """Obtiene todos los anticipos de un chofer específico (con validación de permisos)"""
        try:
            # Verificar permisos: solo admin o el propio chofer
            if not is_admin and driver_id != current_user_id:
                return jsonify({'error': 'No tienes permisos para ver anticipos de este chofer'}), 403
            
            advance_payments = AdvancePayment.query.filter_by(driver_id=driver_id).order_by(AdvancePayment.date.desc()).all()
            return jsonify([ap.to_dict() for ap in advance_payments]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener anticipos del chofer', 'details': str(e)}), 500

    @staticmethod
    def create_advance_payment(data, current_user_id=None, is_admin=False, receipt_file=None):
        """Crea un nuevo anticipo (solo admin puede crear)"""
        try:
            if not is_admin:
                return jsonify({'error': 'Solo los administradores pueden crear anticipos'}), 403
            
            schema = AdvancePaymentSchema()
            validated_data = schema.load(data)
            
            # Establecer el admin_id del usuario autenticado
            validated_data['admin_id'] = current_user_id
            
            # Manejar archivo adjunto si existe
            receipt_url = None
            if receipt_file and receipt_file.filename:
                if AdvancePaymentController._allowed_file(receipt_file.filename):
                    try:
                        # Leer los bytes del archivo
                        file_bytes = receipt_file.read()
                        
                        # Subir a Supabase Storage
                        receipt_url = supabase_storage.upload_file(
                            file_bytes=file_bytes,
                            filename=receipt_file.filename,
                            folder='advance_receipts'
                        )
                    except Exception as e:
                        return jsonify({
                            'error': 'Error al subir el archivo',
                            'details': str(e)
                        }), 500
                else:
                    return jsonify({
                        'error': 'Tipo de archivo no permitido',
                        'details': 'Solo se permiten archivos PDF, PNG, JPG y JPEG'
                    }), 400
            
            if receipt_url:
                validated_data['receipt'] = receipt_url
            
            advance_payment = AdvancePayment(**validated_data)
            db.session.add(advance_payment)
            db.session.commit()

            # Notificar al chofer sobre el adelanto recibido
            try:
                NotificationController.create_for_user(
                    user_id=advance_payment.driver_id,
                    title='Adelanto recibido',
                    message=f"Recibiste un adelanto de ${advance_payment.amount:.2f} el {advance_payment.date.strftime('%d/%m/%Y')}.",
                    notif_type='advance_payment',
                    dedupe_key=f"advance_payment:{advance_payment.id}",
                    data={
                        'advance_payment_id': advance_payment.id,
                        'amount': advance_payment.amount,
                        'date': advance_payment.date.isoformat() if advance_payment.date else None
                    }
                )
            except Exception as e:
                print(f"Error creando notificación de adelanto {advance_payment.id}: {str(e)}")
            
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
            
            # Eliminar archivo de Supabase si existe
            if advance_payment.receipt:
                try:
                    supabase_storage.delete_file(advance_payment.receipt)
                except Exception as e:
                    print(f"Error eliminando archivo de Supabase: {str(e)}")
            
            db.session.delete(advance_payment)
            db.session.commit()
            
            return jsonify({'message': 'Anticipo eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar anticipo', 'details': str(e)}), 500
