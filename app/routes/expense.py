from flask import Blueprint, jsonify, request, abort
from app.models import Expense
from app.db import db

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

# GET all expenses
@expense_bp.route('/', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    result = []
    for e in expenses:
        result.append({
            'id': e.id,
            'trip_id': e.trip_id,
            'expense_type': e.expense_type,
            'date': e.date.isoformat() if e.date else None,
            'amount': e.amount,
            'description': e.description,
            'receipt_url': e.receipt_url,
            'fine_municipality': e.fine_municipality,
            'repair_type': e.repair_type,
            'fuel_liters': e.fuel_liters,
            'toll_type': e.toll_type,
            'toll_paid_by': e.toll_paid_by
        })
    return jsonify(result)

# GET one expense
@expense_bp.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    e = Expense.query.get_or_404(expense_id)
    return jsonify({
        'id': e.id,
        'trip_id': e.trip_id,
        'expense_type': e.expense_type,
        'date': e.date.isoformat() if e.date else None,
        'amount': e.amount,
        'description': e.description,
        'receipt_url': e.receipt_url,
        'fine_municipality': e.fine_municipality,
        'repair_type': e.repair_type,
        'fuel_liters': e.fuel_liters,
        'toll_type': e.toll_type,
        'toll_paid_by': e.toll_paid_by
    })

# CREATE expense
@expense_bp.route('/', methods=['POST'])
def create_expense():
    data = request.get_json()
    expense = Expense(
        trip_id=data.get('trip_id'),
        expense_type=data.get('expense_type'),
        date=data.get('date'),
        amount=data.get('amount'),
        description=data.get('description'),
        receipt_url=data.get('receipt_url'),
        fine_municipality=data.get('fine_municipality'),
        repair_type=data.get('repair_type'),
        fuel_liters=data.get('fuel_liters'),
        toll_type=data.get('toll_type'),
        toll_paid_by=data.get('toll_paid_by')
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({'message': 'Expense creado', 'id': expense.id}), 201

# UPDATE expense
@expense_bp.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    data = request.get_json()
    for field in ['trip_id', 'expense_type', 'date', 'amount', 'description', 'receipt_url', 'fine_municipality', 'repair_type', 'fuel_liters', 'toll_type', 'toll_paid_by']:
        if field in data:
            setattr(expense, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Expense actualizado'})

# DELETE expense
@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense eliminado'})
