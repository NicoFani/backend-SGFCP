from .driver import driver_bp
from .truck import truck_bp  
from .trip import trip_bp
from .expense import expense_bp
from .advance_payment import advance_payment_bp
from .app_user import app_user_bp
from .client import client_bp
from .commission_percentage import commission_percentage_bp
from .driver_truck import driver_truck_bp
from .km_rate import km_rate_bp
from .load_owner import load_owner_bp
from .monthly_summary import monthly_summary_bp
from .auth import auth_bp

__all__ = [
    'driver_bp',
    'truck_bp', 
    'trip_bp',
    'expense_bp',
    'advance_payment_bp',
    'app_user_bp',
    'client_bp',
    'commission_percentage_bp',
    'driver_truck_bp',
    'km_rate_bp',
    'load_owner_bp',
    'monthly_summary_bp',
    'auth_bp'
]
