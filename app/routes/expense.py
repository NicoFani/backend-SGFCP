from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers import ExpenseController
from ..utils import admin_required

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

# GET all expenses (filtrados por conductor si no es admin)
@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return ExpenseController.get_all_expenses(current_user_id, is_admin)

# GET one expense (solo el propio gasto o admin)
@expense_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return ExpenseController.get_expense_by_id(expense_id, current_user_id, is_admin)

# CREATE expense (admin y choferes pueden crear gastos)
@expense_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return ExpenseController.create_expense(request.get_json(), current_user_id, is_admin)

# UPDATE expense (admin y choferes pueden editar sus propios gastos)
@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return ExpenseController.update_expense(expense_id, request.get_json(), current_user_id, is_admin)

# DELETE expense (solo admin)
@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_expense(expense_id):
    return ExpenseController.delete_expense(expense_id)

# GET expenses by trip
@expense_bp.route('/trip/<int:trip_id>', methods=['GET'])
def get_expenses_by_trip(trip_id):
    return ExpenseController.get_expenses_by_trip(trip_id)

# GET expenses by type
@expense_bp.route('/type/<string:expense_type>', methods=['GET'])
def get_expenses_by_type(expense_type):
    return ExpenseController.get_expenses_by_type(expense_type)