from flask import Blueprint, jsonify, request, abort
from app.models import Driver
from app.db import db

driver_bp = Blueprint('driver', __name__, url_prefix='/drivers')

# GET all drivers
@driver_bp.route('/', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    result = []
    for d in drivers:
        result.append({
            'id': d.id,
            'dni': d.dni,
            'cuil': d.cuil,
            'phone_number': d.phone_number,
            'cbu': d.cbu,
            'active': d.active,
            'commission': d.commission,
            'enrollment_date': d.enrollment_date.isoformat() if d.enrollment_date else None,
            'termination_date': d.termination_date.isoformat() if d.termination_date else None,
            'driver_license_due_date': d.driver_license_due_date.isoformat() if d.driver_license_due_date else None,
            'medical_exam_due_date': d.medical_exam_due_date.isoformat() if d.medical_exam_due_date else None
        })
    return jsonify(result)

# GET one driver
@driver_bp.route('/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    d = Driver.query.get_or_404(driver_id)
    return jsonify({
        'id': d.id,
        'dni': d.dni,
        'cuil': d.cuil,
        'phone_number': d.phone_number,
        'cbu': d.cbu,
        'active': d.active,
        'commission': d.commission,
        'enrollment_date': d.enrollment_date.isoformat() if d.enrollment_date else None,
        'termination_date': d.termination_date.isoformat() if d.termination_date else None,
        'driver_license_due_date': d.driver_license_due_date.isoformat() if d.driver_license_due_date else None,
        'medical_exam_due_date': d.medical_exam_due_date.isoformat() if d.medical_exam_due_date else None
    })

# CREATE driver
@driver_bp.route('/', methods=['POST'])
def create_driver():
    data = request.get_json()
    if not data or 'id' not in data:
        abort(400, 'Falta id (app_user.id)')
    driver = Driver(
        id=data['id'],
        dni=data.get('dni'),
        cuil=data.get('cuil'),
        phone_number=data.get('phone_number'),
        cbu=data.get('cbu'),
        active=data.get('active', True),
        commission=data.get('commission', 0),
        enrollment_date=data.get('enrollment_date'),
        termination_date=data.get('termination_date'),
        driver_license_due_date=data.get('driver_license_due_date'),
        medical_exam_due_date=data.get('medical_exam_due_date')
    )
    db.session.add(driver)
    db.session.commit()
    return jsonify({'message': 'Driver creado', 'id': driver.id}), 201

# UPDATE driver
@driver_bp.route('/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    data = request.get_json()
    for field in ['dni', 'cuil', 'phone_number', 'cbu', 'active', 'commission', 'enrollment_date', 'termination_date', 'driver_license_due_date', 'medical_exam_due_date']:
        if field in data:
            setattr(driver, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Driver actualizado'})

# DELETE driver
@driver_bp.route('/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    return jsonify({'message': 'Driver eliminado'})
