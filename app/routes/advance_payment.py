from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers.advance_payment import AdvancePaymentController
from ..utils import admin_required

advance_payment_bp = Blueprint('advance_payment', __name__, url_prefix='/advance-payments')

@advance_payment_bp.route('/', methods=['GET'])
@jwt_required()
def get_advance_payments():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return AdvancePaymentController.get_all_advance_payments(current_user_id, is_admin)

@advance_payment_bp.route('/driver/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_advance_payments_by_driver(driver_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return AdvancePaymentController.get_advance_payments_by_driver(driver_id, current_user_id, is_admin)

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['GET'])
@jwt_required()
def get_advance_payment(advance_payment_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return AdvancePaymentController.get_advance_payment_by_id(advance_payment_id, current_user_id, is_admin)

@advance_payment_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required()
def create_advance_payment():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    
    # Verificar si hay archivo adjunto
    receipt_file = request.files.get('receipt') if request.files else None
    
    # Obtener datos del formulario o JSON
    if receipt_file:
        # Con archivo: datos vienen como form-data
        data = request.form.to_dict()
    else:
        # Sin archivo: datos vienen como JSON
        data = request.get_json()
    
    return AdvancePaymentController.create_advance_payment(
        data, current_user_id, is_admin, receipt_file
    )

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_advance_payment(advance_payment_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return AdvancePaymentController.update_advance_payment(advance_payment_id, request.get_json(), current_user_id, is_admin)

@advance_payment_bp.route('/<int:advance_payment_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_advance_payment(advance_payment_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return AdvancePaymentController.delete_advance_payment(advance_payment_id, current_user_id, is_admin)
