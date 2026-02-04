from .driver import driver_bp
from .truck import truck_bp  
from .trip import trip_bp
from .expense import expense_bp
from .advance_payment import advance_payment_bp
from .app_user import app_user_bp
from .client import client_bp
from .load_type import load_type_bp
from .commission_percentage import commission_percentage_bp
from .driver_truck import driver_truck_bp
from .km_rate import km_rate_bp
from .load_owner import load_owner_bp
from .monthly_summary import monthly_summary_bp
from .auth import auth_bp
from .payroll_period import payroll_period_bp
from .payroll_summary import payroll_summary_bp
from .payroll_adjustment import payroll_adjustment_bp
from .payroll_settings import payroll_settings_bp
from .driver_commission import driver_commission_bp
from .minimum_guaranteed import minimum_guaranteed_bp
from .payroll_other_item import payroll_other_item_bp
from .notification import notification_bp

__all__ = [
    'driver_bp',
    'truck_bp', 
    'trip_bp',
    'expense_bp',
    'advance_payment_bp',
    'app_user_bp',
    'client_bp',
    'load_type_bp',
    'commission_percentage_bp',
    'driver_truck_bp',
    'km_rate_bp',
    'load_owner_bp',
    'monthly_summary_bp',
    'auth_bp',
    'payroll_period_bp',
    'payroll_summary_bp',
    'payroll_adjustment_bp',
    'payroll_settings_bp',
    'driver_commission_bp',
    'minimum_guaranteed_bp',
    'payroll_other_item_bp',
    'notification_bp'
]
