# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.commission_percentage import CommissionPercentage
from ..models.base import db
from ..schemas.commission_percentage import CommissionPercentageSchema, CommissionPercentageUpdateSchema

class CommissionPercentageController:
    
    @staticmethod
    def get_all_commission_percentages():
        """Obtiene todos los porcentajes de comisión"""
        try:
            percentages = CommissionPercentage.query.all()
            return jsonify([p.to_dict() for p in percentages]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener porcentajes de comisión', 'details': str(e)}), 500

    @staticmethod
    def get_commission_percentage_by_id(percentage_id):
        """Obtiene un porcentaje de comisión por ID"""
        try:
            percentage = CommissionPercentage.query.get_or_404(percentage_id)
            return jsonify(percentage.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Porcentaje de comisión no encontrado'}), 404

    @staticmethod
    def create_commission_percentage(data):
        """Crea un nuevo porcentaje de comisión"""
        try:
            schema = CommissionPercentageSchema()
            validated_data = schema.load(data)
            
            percentage = CommissionPercentage(**validated_data)
            db.session.add(percentage)
            db.session.commit()
            
            return jsonify({
                'message': 'Porcentaje de comisión creado exitosamente',
                'commission_percentage': percentage.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear porcentaje de comisión', 'details': str(e)}), 500

    @staticmethod
    def update_commission_percentage(percentage_id, data):
        """Actualiza un porcentaje de comisión existente"""
        try:
            percentage = CommissionPercentage.query.get_or_404(percentage_id)
            
            schema = CommissionPercentageUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(percentage, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Porcentaje de comisión actualizado exitosamente',
                'commission_percentage': percentage.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar porcentaje de comisión', 'details': str(e)}), 500

    @staticmethod
    def delete_commission_percentage(percentage_id):
        """Elimina un porcentaje de comisión"""
        try:
            percentage = CommissionPercentage.query.get_or_404(percentage_id)
            db.session.delete(percentage)
            db.session.commit()
            
            return jsonify({'message': 'Porcentaje de comisión eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar porcentaje de comisión', 'details': str(e)}), 500
