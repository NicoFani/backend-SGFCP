from flask import Blueprint, request
from ..controllers.advance_payment import AdvancePaymentController

advance_payment_bp = Blueprint('advance_payment', __name__, url_prefix='/advance-payments')

@advance_payment_bp.route('/', methods=['GET'])
def get_advance_payments():
    return AdvancePaymentController.get_all_advance_payments()

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['GET'])
def get_advance_payment(advance_payment_id):
    return AdvancePaymentController.get_advance_payment_by_id(advance_payment_id)

@advance_payment_bp.route('/', methods=['POST'])
def create_advance_payment():
    return AdvancePaymentController.create_advance_payment(request.get_json())

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['PUT'])
def update_advance_payment(advance_payment_id):
    return AdvancePaymentController.update_advance_payment(advance_payment_id, request.get_json())

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['DELETE'])
def delete_advance_payment(advance_payment_id):
    return AdvancePaymentController.delete_advance_payment(advance_payment_id)
