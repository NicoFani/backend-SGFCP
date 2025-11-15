# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.km_rate import KmRate
from ..models.base import db
from ..schemas.km_rate import KmRateSchema, KmRateUpdateSchema

class KmRateController:
    
    @staticmethod
    def get_all_km_rates():
        """Obtiene todas las tarifas por kilómetro"""
        try:
            rates = KmRate.query.all()
            return jsonify([rate.to_dict() for rate in rates]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener tarifas', 'details': str(e)}), 500

    @staticmethod
    def get_km_rate_by_id(rate_id):
        """Obtiene una tarifa por ID"""
        try:
            rate = KmRate.query.get_or_404(rate_id)
            return jsonify(rate.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Tarifa no encontrada'}), 404

    @staticmethod
    def create_km_rate(data):
        """Crea una nueva tarifa por kilómetro"""
        try:
            schema = KmRateSchema()
            validated_data = schema.load(data)
            
            rate = KmRate(**validated_data)
            db.session.add(rate)
            db.session.commit()
            
            return jsonify({
                'message': 'Tarifa creada exitosamente',
                'km_rate': rate.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear tarifa', 'details': str(e)}), 500

    @staticmethod
    def update_km_rate(rate_id, data):
        """Actualiza una tarifa existente"""
        try:
            rate = KmRate.query.get_or_404(rate_id)
            
            schema = KmRateUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(rate, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Tarifa actualizada exitosamente',
                'km_rate': rate.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar tarifa', 'details': str(e)}), 500

    @staticmethod
    def delete_km_rate(rate_id):
        """Elimina una tarifa"""
        try:
            rate = KmRate.query.get_or_404(rate_id)
            db.session.delete(rate)
            db.session.commit()
            
            return jsonify({'message': 'Tarifa eliminada exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar tarifa', 'details': str(e)}), 500
