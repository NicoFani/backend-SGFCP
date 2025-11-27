# -*- coding: utf-8 -*-
"""
Decoradores personalizados para autorización
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt

def admin_required():
    """
    Decorador que requiere que el usuario sea administrador
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_admin', False):
                return jsonify({'error': 'Se requieren permisos de administrador'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def owner_or_admin_required(get_owner_id):
    """
    Decorador que permite acceso al propietario del recurso o a un admin
    
    Args:
        get_owner_id: función que recibe los kwargs de la ruta y retorna el user_id del propietario
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            is_admin = claims.get('is_admin', False)
            
            # Si es admin, permitir
            if is_admin:
                return fn(*args, **kwargs)
            
            # Obtener el ID del propietario del recurso
            resource_owner_id = get_owner_id(kwargs)
            
            # Verificar si el usuario actual es el propietario
            if current_user_id != resource_owner_id:
                return jsonify({'error': 'No tienes permisos para acceder a este recurso'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def driver_or_admin_required():
    """
    Decorador que verifica que el usuario autenticado sea el conductor del recurso o admin
    Se usa cuando el recurso pertenece a un conductor (viajes, gastos, etc.)
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            is_admin = claims.get('is_admin', False)
            
            # Si es admin, permitir
            if is_admin:
                return fn(*args, **kwargs)
            
            # Agregar el user_id al contexto para que los controllers lo usen
            kwargs['current_user_id'] = current_user_id
            kwargs['is_admin'] = is_admin
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
