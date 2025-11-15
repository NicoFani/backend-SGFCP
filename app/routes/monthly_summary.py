from flask import Blueprint, request
from ..controllers.monthly_summary import MonthlySummaryController

monthly_summary_bp = Blueprint('monthly_summary', __name__, url_prefix='/monthly-summaries')

@monthly_summary_bp.route('/', methods=['GET'])
def get_monthly_summaries():
    return MonthlySummaryController.get_all_monthly_summaries()

@monthly_summary_bp.route('/<int:summary_id>', methods=['GET'])
def get_monthly_summary(summary_id):
    return MonthlySummaryController.get_monthly_summary_by_id(summary_id)

@monthly_summary_bp.route('/', methods=['POST'])
def create_monthly_summary():
    return MonthlySummaryController.create_monthly_summary(request.get_json())

@monthly_summary_bp.route('/<int:summary_id>', methods=['PUT'])
def update_monthly_summary(summary_id):
    return MonthlySummaryController.update_monthly_summary(summary_id, request.get_json())

@monthly_summary_bp.route('/<int:summary_id>', methods=['DELETE'])
def delete_monthly_summary(summary_id):
    return MonthlySummaryController.delete_monthly_summary(summary_id)
