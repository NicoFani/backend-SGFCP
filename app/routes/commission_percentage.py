from flask import Blueprint, request
from ..controllers.commission_percentage import CommissionPercentageController

commission_percentage_bp = Blueprint('commission_percentage', __name__, url_prefix='/commission-percentages')

@commission_percentage_bp.route('/', methods=['GET'])
def get_commission_percentages():
    return CommissionPercentageController.get_all_commission_percentages()

@commission_percentage_bp.route('/<int:percentage_id>', methods=['GET'])
def get_commission_percentage(percentage_id):
    return CommissionPercentageController.get_commission_percentage_by_id(percentage_id)

@commission_percentage_bp.route('/', methods=['POST'])
def create_commission_percentage():
    return CommissionPercentageController.create_commission_percentage(request.get_json())

@commission_percentage_bp.route('/<int:percentage_id>', methods=['PUT'])
def update_commission_percentage(percentage_id):
    return CommissionPercentageController.update_commission_percentage(percentage_id, request.get_json())

@commission_percentage_bp.route('/<int:percentage_id>', methods=['DELETE'])
def delete_commission_percentage(percentage_id):
    return CommissionPercentageController.delete_commission_percentage(percentage_id)
