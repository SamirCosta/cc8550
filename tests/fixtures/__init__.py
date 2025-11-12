"""
Módulo de Fixtures para Testes

Este módulo centraliza todas as fixtures utilizadas nos testes,
organizadas por categoria para melhor manutenibilidade.
"""
from .database import *
from .repositories import *
from .models import *
from .test_data import *

__all__ = [
    # Database
    'test_db',

    # Repositories
    'car_repository',
    'customer_repository',
    'rental_repository',
    'payment_repository',
    'maintenance_repository',

    # Sample Models
    'sample_car',
    'sample_customer',
    'sample_rental',
    'sample_payment',
    'sample_maintenance',

    # Created Models
    'create_test_car',
    'create_test_customer',
    'create_test_rental',
    'create_test_payment',

    # Test Data
    'valid_cpfs',
    'invalid_cpfs',
    'valid_emails',
    'invalid_emails',
    'valid_phones',
    'invalid_phones',
    'valid_license_plates',
    'invalid_license_plates',
]
