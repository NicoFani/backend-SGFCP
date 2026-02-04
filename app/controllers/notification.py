# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from ..models.notification import Notification
from ..models.app_user import AppUser
from ..models.driver import Driver
from ..models.driver_truck import DriverTruck
from ..models.truck import Truck
from ..models.base import db

DOC_WARNING_DAYS = 30


class NotificationController:

    @staticmethod
    def _add_notification(user_id, title, message, notif_type, dedupe_key=None, data=None):
        if dedupe_key:
            existing = Notification.query.filter_by(user_id=user_id, dedupe_key=dedupe_key).first()
            if existing:
                return False
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            dedupe_key=dedupe_key,
            data=data,
        )
        db.session.add(notification)
        return True

    @staticmethod
    def create_for_user(user_id, title, message, notif_type, dedupe_key=None, data=None, commit=True):
        try:
            created = NotificationController._add_notification(
                user_id, title, message, notif_type, dedupe_key, data
            )
            if created and commit:
                db.session.commit()
            return created
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def create_for_admins(title, message, notif_type, dedupe_key=None, data=None, commit=True):
        try:
            admins = AppUser.query.filter_by(is_admin=True, is_active=True).all()
            created_any = False
            for admin in admins:
                created = NotificationController._add_notification(
                    admin.id, title, message, notif_type, dedupe_key, data
                )
                created_any = created_any or created
            if created_any and commit:
                db.session.commit()
            return created_any
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def get_notifications(current_user_id, is_admin=False):
        try:
            NotificationController.ensure_document_notifications(current_user_id, is_admin)
            notifications = Notification.query.filter_by(user_id=current_user_id).order_by(
                Notification.created_at.desc()
            ).all()
            return jsonify([n.to_dict() for n in notifications]), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener notificaciones', 'details': str(e)}), 500

    @staticmethod
    def get_unread_count(current_user_id, is_admin=False):
        try:
            NotificationController.ensure_document_notifications(current_user_id, is_admin)
            count = Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
            return jsonify({'count': count}), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener conteo', 'details': str(e)}), 500

    @staticmethod
    def mark_as_read(notification_id, current_user_id):
        try:
            notification = Notification.query.get_or_404(notification_id)
            if notification.user_id != current_user_id:
                return jsonify({'error': 'No tienes permisos para modificar esta notificación'}), 403

            if not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()

            return jsonify({
                'message': 'Notificación marcada como leída',
                'notification': notification.to_dict()
            }), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar notificación', 'details': str(e)}), 500

    @staticmethod
    def mark_all_as_read(current_user_id):
        try:
            Notification.query.filter_by(user_id=current_user_id, is_read=False).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            db.session.commit()
            return jsonify({'message': 'Notificaciones marcadas como leídas'}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar notificaciones', 'details': str(e)}), 500

    @staticmethod
    def ensure_document_notifications(current_user_id, is_admin):
        try:
            today = date.today()
            warning_date = today + timedelta(days=DOC_WARNING_DAYS)
            created_any = False

            if is_admin:
                drivers = Driver.query.filter_by(active=True).all()
                for driver in drivers:
                    created_any |= NotificationController._notify_driver_docs_for_admin(driver, today, warning_date)

                trucks = Truck.query.filter_by(operational=True).all()
                for truck in trucks:
                    created_any |= NotificationController._notify_truck_docs_for_admin(truck, today, warning_date)
            else:
                driver = Driver.query.get(current_user_id)
                if driver:
                    created_any |= NotificationController._notify_driver_docs_for_driver(driver, today, warning_date)
                    created_any |= NotificationController._notify_current_truck_docs_for_driver(driver, today, warning_date)

            if created_any:
                db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    @staticmethod
    def _notify_driver_docs_for_admin(driver, today, warning_date):
        created_any = False
        driver_name = f"{driver.user.name} {driver.user.surname}" if driver.user else f"Chofer {driver.id}"

        created_any |= NotificationController._create_doc_notification(
            user_scope='admin',
            target_user_id=None,
            entity_type='driver',
            entity_id=driver.id,
            field_name='driver_license_due_date',
            field_label='Licencia de conducir',
            due_date=driver.driver_license_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'driver_name': driver_name},
            admin_message_prefix=f"{driver_name}"
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='admin',
            target_user_id=None,
            entity_type='driver',
            entity_id=driver.id,
            field_name='medical_exam_due_date',
            field_label='Psicofísico',
            due_date=driver.medical_exam_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'driver_name': driver_name},
            admin_message_prefix=f"{driver_name}"
        )

        return created_any

    @staticmethod
    def _notify_truck_docs_for_admin(truck, today, warning_date):
        created_any = False
        truck_label = f"Camión {truck.plate}"

        created_any |= NotificationController._create_doc_notification(
            user_scope='admin',
            target_user_id=None,
            entity_type='truck',
            entity_id=truck.id,
            field_name='service_due_date',
            field_label='Service',
            due_date=truck.service_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate},
            admin_message_prefix=truck_label
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='admin',
            target_user_id=None,
            entity_type='truck',
            entity_id=truck.id,
            field_name='vtv_due_date',
            field_label='VTV',
            due_date=truck.vtv_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate},
            admin_message_prefix=truck_label
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='admin',
            target_user_id=None,
            entity_type='truck',
            entity_id=truck.id,
            field_name='plate_due_date',
            field_label='Vencimiento de patente',
            due_date=truck.plate_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate},
            admin_message_prefix=truck_label
        )

        return created_any

    @staticmethod
    def _notify_driver_docs_for_driver(driver, today, warning_date):
        created_any = False
        created_any |= NotificationController._create_doc_notification(
            user_scope='driver',
            target_user_id=driver.id,
            entity_type='driver',
            entity_id=driver.id,
            field_name='driver_license_due_date',
            field_label='Licencia de conducir',
            due_date=driver.driver_license_due_date,
            today=today,
            warning_date=warning_date
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='driver',
            target_user_id=driver.id,
            entity_type='driver',
            entity_id=driver.id,
            field_name='medical_exam_due_date',
            field_label='Psicofísico',
            due_date=driver.medical_exam_due_date,
            today=today,
            warning_date=warning_date
        )

        return created_any

    @staticmethod
    def _notify_current_truck_docs_for_driver(driver, today, warning_date):
        assignment = DriverTruck.query.filter_by(driver_id=driver.id).order_by(DriverTruck.date.desc()).first()
        if not assignment:
            return False

        truck = Truck.query.get(assignment.truck_id)
        if not truck:
            return False

        created_any = False
        created_any |= NotificationController._create_doc_notification(
            user_scope='driver',
            target_user_id=driver.id,
            entity_type='truck',
            entity_id=truck.id,
            field_name='service_due_date',
            field_label='Service',
            due_date=truck.service_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate}
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='driver',
            target_user_id=driver.id,
            entity_type='truck',
            entity_id=truck.id,
            field_name='vtv_due_date',
            field_label='VTV',
            due_date=truck.vtv_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate}
        )

        created_any |= NotificationController._create_doc_notification(
            user_scope='driver',
            target_user_id=driver.id,
            entity_type='truck',
            entity_id=truck.id,
            field_name='plate_due_date',
            field_label='Vencimiento de patente',
            due_date=truck.plate_due_date,
            today=today,
            warning_date=warning_date,
            extra_context={'truck_plate': truck.plate}
        )

        return created_any

    @staticmethod
    def _create_doc_notification(
        user_scope,
        target_user_id,
        entity_type,
        entity_id,
        field_name,
        field_label,
        due_date,
        today,
        warning_date,
        extra_context=None,
        admin_message_prefix=None
    ):
        if not due_date:
            return False

        if due_date < today:
            status = 'expired'
            title = f"{field_label} vencido"
            base_message = f"{field_label} vencido el {due_date.strftime('%d/%m/%Y')}."
            notif_type = 'document_expired'
        elif due_date <= warning_date:
            status = 'expiring'
            title = f"{field_label} por vencer"
            base_message = f"{field_label} vence el {due_date.strftime('%d/%m/%Y')}."
            notif_type = 'document_expiring'
        else:
            return False

        if user_scope == 'admin':
            if not admin_message_prefix:
                admin_message_prefix = 'Documentación'
            message = f"{admin_message_prefix}: {base_message}"
            admins = AppUser.query.filter_by(is_admin=True, is_active=True).all()
            created_any = False
            for admin in admins:
                dedupe_key = f"doc:{status}:{entity_type}:{entity_id}:{field_name}:{due_date.isoformat()}"
                created = NotificationController._add_notification(
                    admin.id,
                    title,
                    message,
                    notif_type,
                    dedupe_key=dedupe_key,
                    data={
                        'entity_type': entity_type,
                        'entity_id': entity_id,
                        'field': field_name,
                        'due_date': due_date.isoformat(),
                        **(extra_context or {})
                    }
                )
                created_any = created_any or created
            return created_any

        if not target_user_id:
            return False

        dedupe_key = f"doc:{status}:{entity_type}:{entity_id}:{field_name}:{due_date.isoformat()}"
        return NotificationController._add_notification(
            target_user_id,
            title,
            base_message,
            notif_type,
            dedupe_key=dedupe_key,
            data={
                'entity_type': entity_type,
                'entity_id': entity_id,
                'field': field_name,
                'due_date': due_date.isoformat(),
                **(extra_context or {})
            }
        )
