from flask import Blueprint, request
from ..controllers.km_rate import KmRateController

km_rate_bp = Blueprint('km_rate', __name__, url_prefix='/km-rates')

@km_rate_bp.route('/', methods=['GET'])
def get_km_rates():
    return KmRateController.get_all_km_rates()

@km_rate_bp.route('/<int:rate_id>', methods=['GET'])
def get_km_rate(rate_id):
    return KmRateController.get_km_rate_by_id(rate_id)

@km_rate_bp.route('/', methods=['POST'])
def create_km_rate():
    return KmRateController.create_km_rate(request.get_json())

@km_rate_bp.route('/<int:rate_id>', methods=['PUT'])
def update_km_rate(rate_id):
    return KmRateController.update_km_rate(rate_id, request.get_json())

@km_rate_bp.route('/<int:rate_id>', methods=['DELETE'])
def delete_km_rate(rate_id):
    return KmRateController.delete_km_rate(rate_id)
