from app.db import db
from app.models.load_type import LoadType
from app.schemas.load_type import LoadTypeSchema, LoadTypeUpdateSchema
from marshmallow import ValidationError

def get_all_load_types():
    """Obtener todos los tipos de carga"""
    load_types = LoadType.query.order_by(LoadType.name).all()
    return [lt.to_dict() for lt in load_types]

def get_load_type(load_type_id):
    """Obtener un tipo de carga por ID"""
    load_type = LoadType.query.get(load_type_id)
    if not load_type:
        return None
    return load_type.to_dict()

def create_load_type(data):
    """Crear un nuevo tipo de carga"""
    schema = LoadTypeSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        raise ValueError(str(err.messages))
    
    # Verificar si ya existe un tipo de carga con ese nombre
    existing = LoadType.query.filter_by(name=validated_data['name']).first()
    if existing:
        raise ValueError(f"Ya existe un tipo de carga con el nombre '{validated_data['name']}'")
    
    load_type = LoadType(**validated_data)
    db.session.add(load_type)
    db.session.commit()
    
    return load_type.to_dict()

def update_load_type(load_type_id, data):
    """Actualizar un tipo de carga"""
    load_type = LoadType.query.get(load_type_id)
    if not load_type:
        return None
    
    schema = LoadTypeUpdateSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        raise ValueError(str(err.messages))
    
    # Si se está actualizando el nombre, verificar que no exista otro con ese nombre
    if 'name' in validated_data and validated_data['name'] != load_type.name:
        existing = LoadType.query.filter_by(name=validated_data['name']).first()
        if existing:
            raise ValueError(f"Ya existe un tipo de carga con el nombre '{validated_data['name']}'")
    
    for key, value in validated_data.items():
        setattr(load_type, key, value)
    
    db.session.commit()
    return load_type.to_dict()

def delete_load_type(load_type_id):
    """Eliminar un tipo de carga"""
    load_type = LoadType.query.get(load_type_id)
    if not load_type:
        return None
    
    # Verificar si hay viajes asociados
    from app.models.trip import Trip
    trips_count = Trip.query.filter_by(load_type_id=load_type_id).count()
    if trips_count > 0:
        raise ValueError(f"No se puede eliminar el tipo de carga porque tiene {trips_count} viaje(s) asociado(s)")
    
    db.session.delete(load_type)
    db.session.commit()
    return True
