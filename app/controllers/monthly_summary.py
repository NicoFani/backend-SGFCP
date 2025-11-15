# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.monthly_summary import MonthlySummary
from ..models.base import db
from ..schemas.monthly_summary import MonthlySummarySchema, MonthlySummaryUpdateSchema

class MonthlySummaryController:
    
    @staticmethod
    def get_all_monthly_summaries():
        """Obtiene todos los resúmenes mensuales"""
        try:
            summaries = MonthlySummary.query.all()
            return jsonify([summary.to_dict() for summary in summaries]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener resúmenes mensuales', 'details': str(e)}), 500

    @staticmethod
    def get_monthly_summary_by_id(summary_id):
        """Obtiene un resumen mensual por ID"""
        try:
            summary = MonthlySummary.query.get_or_404(summary_id)
            return jsonify(summary.to_dict()), 200
        except Exception as e:
            return jsonify({'error': 'Resumen mensual no encontrado'}), 404

    @staticmethod
    def create_monthly_summary(data):
        """Crea un nuevo resumen mensual"""
        try:
            schema = MonthlySummarySchema()
            validated_data = schema.load(data)
            
            summary = MonthlySummary(**validated_data)
            db.session.add(summary)
            db.session.commit()
            
            return jsonify({
                'message': 'Resumen mensual creado exitosamente',
                'monthly_summary': summary.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear resumen mensual', 'details': str(e)}), 500

    @staticmethod
    def update_monthly_summary(summary_id, data):
        """Actualiza un resumen mensual existente"""
        try:
            summary = MonthlySummary.query.get_or_404(summary_id)
            
            schema = MonthlySummaryUpdateSchema()
            validated_data = schema.load(data)
            
            for field, value in validated_data.items():
                setattr(summary, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Resumen mensual actualizado exitosamente',
                'monthly_summary': summary.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar resumen mensual', 'details': str(e)}), 500

    @staticmethod
    def delete_monthly_summary(summary_id):
        """Elimina un resumen mensual"""
        try:
            summary = MonthlySummary.query.get_or_404(summary_id)
            db.session.delete(summary)
            db.session.commit()
            
            return jsonify({'message': 'Resumen mensual eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar resumen mensual', 'details': str(e)}), 500
