from flask import Blueprint, request
from ..controllers import ExpenseController

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

# GET all expenses
@expense_bp.route('/', methods=['GET'])
def get_expenses():
    return ExpenseController.get_all_expenses()

# GET one expense
@expense_bp.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    return ExpenseController.get_expense_by_id(expense_id)

# CREATE expense
@expense_bp.route('/', methods=['POST'])
def create_expense():
    return ExpenseController.create_expense(request.get_json())

# UPDATE expense
@expense_bp.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    return ExpenseController.update_expense(expense_id, request.get_json())

# DELETE expense
@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
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