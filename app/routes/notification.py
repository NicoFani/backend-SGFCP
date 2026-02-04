from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..controllers.notification import NotificationController

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')


@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return NotificationController.get_notifications(current_user_id, is_admin)


@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    current_user_id = int(get_jwt_identity())
    is_admin = get_jwt().get('is_admin', False)
    return NotificationController.get_unread_count(current_user_id, is_admin)


@notification_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_as_read(notification_id):
    current_user_id = int(get_jwt_identity())
    return NotificationController.mark_as_read(notification_id, current_user_id)


@notification_bp.route('/read-all', methods=['PATCH'])
@jwt_required()
def mark_all_read():
    current_user_id = int(get_jwt_identity())
    return NotificationController.mark_all_as_read(current_user_id)
