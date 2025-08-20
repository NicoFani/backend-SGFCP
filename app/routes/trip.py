from flask import Blueprint, jsonify, request, abort
from app.models import Trip
from app.db import db

trip_bp = Blueprint('trip', __name__, url_prefix='/trips')

# GET all trips
@trip_bp.route('/', methods=['GET'])
def get_trips():
    trips = Trip.query.all()
    result = []
    for t in trips:
        result.append({
            'id': t.id,
            'document_number': t.document_number,
            'origin': t.origin,
            'destination': t.destination,
            'estimated_kms': t.estimated_kms,
            'start_date': t.start_date.isoformat() if t.start_date else None,
            'end_date': t.end_date.isoformat() if t.end_date else None,
            'load_weight_on_load': t.load_weight_on_load,
            'load_weight_on_unload': t.load_weight_on_unload,
            'rate_per_ton': t.rate_per_ton,
            'fuel_on_client': t.fuel_on_client,
            'client_advance_payment': t.client_advance_payment,
            'state_id': t.state_id,
            'driver_id': t.driver_id,
            'client_id': t.client_id,
            'load_owner_id': t.load_owner_id
        })
    return jsonify(result)

# GET one trip
@trip_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    t = Trip.query.get_or_404(trip_id)
    return jsonify({
        'id': t.id,
        'document_number': t.document_number,
        'origin': t.origin,
        'destination': t.destination,
        'estimated_kms': t.estimated_kms,
        'start_date': t.start_date.isoformat() if t.start_date else None,
        'end_date': t.end_date.isoformat() if t.end_date else None,
        'load_weight_on_load': t.load_weight_on_load,
        'load_weight_on_unload': t.load_weight_on_unload,
        'rate_per_ton': t.rate_per_ton,
        'fuel_on_client': t.fuel_on_client,
        'client_advance_payment': t.client_advance_payment,
        'state_id': t.state_id,
        'driver_id': t.driver_id,
        'client_id': t.client_id,
        'load_owner_id': t.load_owner_id
    })

# CREATE trip
@trip_bp.route('/', methods=['POST'])
def create_trip():
    data = request.get_json()
    trip = Trip(
        document_number=data.get('document_number'),
        origin=data.get('origin'),
        destination=data.get('destination'),
        estimated_kms=data.get('estimated_kms'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        load_weight_on_load=data.get('load_weight_on_load'),
        load_weight_on_unload=data.get('load_weight_on_unload'),
        rate_per_ton=data.get('rate_per_ton'),
        fuel_on_client=data.get('fuel_on_client'),
        client_advance_payment=data.get('client_advance_payment'),
        state_id=data.get('state_id'),
        driver_id=data.get('driver_id'),
        client_id=data.get('client_id'),
        load_owner_id=data.get('load_owner_id')
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify({'message': 'Trip creado', 'id': trip.id}), 201

# UPDATE trip
@trip_bp.route('/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    data = request.get_json()
    for field in ['document_number', 'origin', 'destination', 'estimated_kms', 'start_date', 'end_date', 'load_weight_on_load', 'load_weight_on_unload', 'rate_per_ton', 'fuel_on_client', 'client_advance_payment', 'state_id', 'driver_id', 'client_id', 'load_owner_id']:
        if field in data:
            setattr(trip, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Trip actualizado'})

# DELETE trip
@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip eliminado'})
