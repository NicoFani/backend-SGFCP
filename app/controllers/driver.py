# -*- coding: utf-8 -*-
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from ..models.driver import Driver
from ..models.base import db
from ..schemas.driver import DriverSchema, DriverUpdateSchema

class DriverController:
    
    @staticmethod
    def get_all_drivers(current_user_id=None, is_admin=False):
        """Obtiene todos los conductores (solo admin puede ver todos)"""
        try:
            if is_admin:
                drivers = Driver.query.all()
            else:
                # Los conductores solo pueden ver su propia información
                drivers = Driver.query.filter_by(id=current_user_id).all()

            drivers_data = [driver.to_dict() for driver in drivers]

            # Estado operativo del chofer: tiene viaje "En curso"
            if drivers_data:
                from ..models.trip import Trip
                driver_ids = [driver['id'] for driver in drivers_data]
                active_rows = db.session.query(Trip.driver_id).filter(
                    Trip.driver_id.in_(driver_ids),
                    Trip.state_id == 'En curso'
                ).distinct().all()
                active_driver_ids = {row[0] for row in active_rows}

                for driver in drivers_data:
                    driver['is_active'] = driver['id'] in active_driver_ids

            return jsonify(drivers_data), 200
        except SQLAlchemyError as e:
            return jsonify({'error': 'Error al obtener conductores', 'details': str(e)}), 500

    @staticmethod
    def get_driver_by_id(driver_id):
        """Obtiene un conductor por ID"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            driver_data = driver.to_dict()

            from ..models.trip import Trip
            has_active_trip = db.session.query(Trip.id).filter(
                Trip.driver_id == driver_id,
                Trip.state_id == 'En curso'
            ).first() is not None
            driver_data['is_active'] = has_active_trip

            return jsonify(driver_data), 200
        except Exception as e:
            return jsonify({'error': 'Conductor no encontrado'}), 404

    @staticmethod
    def create_driver_complete(data):
        """Crea un usuario y conductor en un solo paso"""
        try:
            from ..models.app_user import AppUser
            from app import bcrypt
            import secrets
            import string
            
            # Validar datos requeridos
            if not data.get('cuil'):
                return jsonify({'error': 'CUIL es requerido'}), 400
            if not data.get('cbu'):
                return jsonify({'error': 'CVU/CBU es requerido'}), 400
            if not data.get('phone_number'):
                return jsonify({'error': 'Número de teléfono es requerido'}), 400
            
            # Generar contraseña temporal
            password_chars = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(password_chars) for _ in range(12))
            
            # Crear usuario
            user = AppUser(
                name=data.get('name'),
                surname=data.get('surname'),
                email=data.get('email'),
                password_hash=bcrypt.generate_password_hash(temp_password).decode('utf-8'),
                is_admin=False,
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Obtener el ID del usuario
            
            # Calcular DNI desde CUIL (quitando primer y últimos dígitos)
            cuil = data.get('cuil', '').replace('-', '')
            if len(cuil) != 11:
                db.session.rollback()
                return jsonify({'error': 'CUIL debe tener 11 dígitos'}), 400
            dni = int(cuil[2:10])
            
            # Crear driver con fechas por defecto (1 año desde hoy)
            from datetime import date, timedelta
            today = date.today()
            one_year_later = today + timedelta(days=365)
            
            driver = Driver(
                id=user.id,
                dni=dni,
                cuil=cuil,
                phone_number=data.get('phone_number'),
                cbu=data.get('cbu'),
                active=True,
                enrollment_date=today,
                driver_license_due_date=one_year_later,
                medical_exam_due_date=one_year_later
            )
            db.session.add(driver)
            db.session.flush()  # Obtener el ID del driver para los registros históricos
            
            # Crear registro inicial de comisión (18%)
            from ..models.driver_commission_history import DriverCommissionHistory
            from datetime import datetime
            commission_record = DriverCommissionHistory(
                driver_id=driver.id,
                commission_percentage=0.18,  # 18% guardado como decimal
                effective_from=datetime.now(),
                effective_until=None  # NULL = vigente actualmente
            )
            db.session.add(commission_record)
            
            # Crear registro inicial de mínimo garantizado (1.000.000)
            from ..models.minimum_guaranteed_history import MinimumGuaranteedHistory
            minimum_record = MinimumGuaranteedHistory(
                driver_id=driver.id,
                minimum_guaranteed=1000000.00,  # 1.000.000 pesos
                effective_from=datetime.now(),
                effective_until=None  # NULL = vigente actualmente
            )
            db.session.add(minimum_record)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Conductor creado exitosamente',
                'driver': driver.to_dict(),
                'temp_password': temp_password  # Enviar para que admin se la pase al chofer
            }), 201
            
        except ValidationError as e:
            db.session.rollback()
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear conductor', 'details': str(e)}), 500

    @staticmethod
    def update_driver_basic_data(driver_id, data):
        """Actualiza datos básicos del conductor y su usuario asociado"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            from ..models.app_user import AppUser
            user = AppUser.query.get(driver_id)
            
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Actualizar datos del usuario
            if 'name' in data:
                user.name = data['name']
            if 'surname' in data:
                user.surname = data['surname']
            
            # Actualizar datos del driver
            if 'cuil' in data:
                cuil = data['cuil'].replace('-', '')
                driver.cuil = cuil
                # Actualizar DNI desde CUIL
                driver.dni = int(cuil[2:10]) if len(cuil) == 11 else driver.dni
            
            if 'cbu' in data:
                driver.cbu = data['cbu']
            if 'phone_number' in data:
                driver.phone_number = data['phone_number']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Datos actualizados exitosamente',
                'driver': driver.to_dict()
            }), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar datos', 'details': str(e)}), 500

    @staticmethod
    def create_driver(data):
        """Crea un nuevo conductor"""
        try:
            # Validar datos
            schema = DriverSchema()
            validated_data = schema.load(data)
            
            # Crear conductor
            driver = Driver(**validated_data)
            db.session.add(driver)
            db.session.commit()
            
            return jsonify({
                'message': 'Conductor creado exitosamente',
                'driver': driver.to_dict()
            }), 201
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al crear conductor', 'details': str(e)}), 500

    @staticmethod
    def update_driver(driver_id, data):
        """Actualiza un conductor existente"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            
            # Validar datos
            schema = DriverUpdateSchema()
            validated_data = schema.load(data)
            
            # Actualizar campos
            for field, value in validated_data.items():
                setattr(driver, field, value)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Conductor actualizado exitosamente',
                'driver': driver.to_dict()
            }), 200
            
        except ValidationError as e:
            return jsonify({'error': 'Datos invalidos', 'details': e.messages}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al actualizar conductor', 'details': str(e)}), 500

    @staticmethod
    def delete_driver(driver_id):
        """Elimina un conductor"""
        try:
            driver = Driver.query.get_or_404(driver_id)
            db.session.delete(driver)
            db.session.commit()
            
            return jsonify({'message': 'Conductor eliminado exitosamente'}), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar conductor', 'details': str(e)}), 500