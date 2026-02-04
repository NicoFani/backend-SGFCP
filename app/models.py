# Este archivo permite importar todos los modelos desde un solo lugar

# Importar base (db y enums)
from .models.base import db
from .models.base import (
    calculation_method_enum,
    expense_type_enum, 
    toll_paid_by_enum,
    toll_type_enum,
    trip_state_enum
)

# Importar todos los modelos
from .models.app_user import AppUser
from .models.driver import Driver
from .models.truck import Truck
from .models.trip import Trip
from .models.expense import Expense
from .models.client import Client
from .models.load_owner import LoadOwner
from .models.advance_payment import AdvancePayment
from .models.commission_percentage import CommissionPercentage
from .models.driver_truck import DriverTruck
from .models.km_rate import KmRate
from .models.monthly_summary import MonthlySummary
from .models.notification import Notification

__all__ = [
    'db',
    'calculation_method_enum',
    'expense_type_enum',
    'toll_paid_by_enum', 
    'toll_type_enum',
    'trip_state_enum',
    'AppUser',
    'Driver',
    'Truck',
    'Trip', 
    'Expense',
    'Client',
    'LoadOwner',
    'AdvancePayment',
    'CommissionPercentage',
    'DriverTruck',
    'KmRate',
    'MonthlySummary',
    'Notification'
]

