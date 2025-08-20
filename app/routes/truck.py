from flask import Blueprint, jsonify, request, abort
from app.models import Truck
from app.db import db

truck_bp = Blueprint('truck', __name__, url_prefix='/trucks')

# GET all trucks
@truck_bp.route('/', methods=['GET'])
def get_trucks():
    trucks = Truck.query.all()
    result = []
    for t in trucks:
        result.append({
            'id': t.id,
            'plate': t.plate,
            'operational': t.operational,
            'brand': t.brand,
            'model_name': t.model_name,
            'fabrication_year': t.fabrication_year,
            'service_due_date': t.service_due_date.isoformat() if t.service_due_date else None,
            'vtv_due_date': t.vtv_due_date.isoformat() if t.vtv_due_date else None,
            'plate_due_date': t.plate_due_date.isoformat() if t.plate_due_date else None
        })
    return jsonify(result)

# GET one truck
@truck_bp.route('/<int:truck_id>', methods=['GET'])
def get_truck(truck_id):
    t = Truck.query.get_or_404(truck_id)
    return jsonify({
        'id': t.id,
        'plate': t.plate,
        'operational': t.operational,
        'brand': t.brand,
        'model_name': t.model_name,
        'fabrication_year': t.fabrication_year,
        'service_due_date': t.service_due_date.isoformat() if t.service_due_date else None,
        'vtv_due_date': t.vtv_due_date.isoformat() if t.vtv_due_date else None,
        'plate_due_date': t.plate_due_date.isoformat() if t.plate_due_date else None
    })

# CREATE truck
@truck_bp.route('/', methods=['POST'])
def create_truck():
    data = request.get_json()
    truck = Truck(
        plate=data.get('plate'),
        operational=data.get('operational', True),
        brand=data.get('brand'),
        model_name=data.get('model_name'),
        fabrication_year=data.get('fabrication_year'),
        service_due_date=data.get('service_due_date'),
        vtv_due_date=data.get('vtv_due_date'),
        plate_due_date=data.get('plate_due_date')
    )
    db.session.add(truck)
    db.session.commit()
    return jsonify({'message': 'Truck creado', 'id': truck.id}), 201

# UPDATE truck
@truck_bp.route('/<int:truck_id>', methods=['PUT'])
def update_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    data = request.get_json()
    for field in ['plate', 'operational', 'brand', 'model_name', 'fabrication_year', 'service_due_date', 'vtv_due_date', 'plate_due_date']:
        if field in data:
            setattr(truck, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Truck actualizado'})

# DELETE truck
@truck_bp.route('/<int:truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    db.session.delete(truck)
    db.session.commit()
    return jsonify({'message': 'Truck eliminado'})
