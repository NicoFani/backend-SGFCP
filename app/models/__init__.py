from .base import db
from .app_user import AppUser
from .driver import Driver
from .truck import Truck
from .trip import Trip
from .expense import Expense
from .client import Client
from .load_owner import LoadOwner
from .load_type import LoadType
from .advance_payment import AdvancePayment
from .driver_truck import DriverTruck
from .payroll_period import PayrollPeriod
from .payroll_summary import PayrollSummary
from .payroll_detail import PayrollDetail
from .payroll_settings import PayrollSettings
from .driver_commission_history import DriverCommissionHistory
from .minimum_guaranteed_history import MinimumGuaranteedHistory
from .payroll_other_item import PayrollOtherItem

# Deprecated models (mantener por compatibilidad pero no usar)
from .commission_percentage import CommissionPercentage
from .km_rate import KmRate
from .monthly_summary import MonthlySummary
from .payroll_adjustment import PayrollAdjustment

# Export all models
__all__ = [
    'db',
    'AppUser',
    'Driver', 
    'Truck',
    'Trip',
    'Expense',
    'Client',
    'LoadOwner',
    'LoadType',
    'AdvancePayment',
    'DriverTruck',
    'PayrollPeriod',
    'PayrollSummary',
    'PayrollDetail',
    'PayrollSettings',
    'DriverCommissionHistory',
    'MinimumGuaranteedHistory',
    'PayrollOtherItem',
    # Deprecated
    'CommissionPercentage',
    'KmRate',
    'MonthlySummary',
    'PayrollAdjustment'
]