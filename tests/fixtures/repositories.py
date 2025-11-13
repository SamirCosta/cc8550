"""
Fixtures de Repositórios

Fixtures que fornecem instâncias de repositórios configurados
com banco de dados de teste.
"""
import pytest
from src.repositories import (
    CarRepository,
    CustomerRepository,
    RentalRepository,
    PaymentRepository,
    MaintenanceRepository
)
from .database import test_db


@pytest.fixture
def car_repository(test_db):
    """
    Fixture que retorna um repositório de carros com banco de teste.

    Args:
        test_db: Banco de dados de teste

    Returns:
        CarRepository: Repositório configurado
    """
    return CarRepository(test_db)


@pytest.fixture
def customer_repository(test_db):
    """
    Fixture que retorna um repositório de clientes com banco de teste.

    Args:
        test_db: Banco de dados de teste

    Returns:
        CustomerRepository: Repositório configurado
    """
    return CustomerRepository(test_db)


@pytest.fixture
def rental_repository(test_db):
    """
    Fixture que retorna um repositório de aluguéis com banco de teste.

    Args:
        test_db: Banco de dados de teste

    Returns:
        RentalRepository: Repositório configurado
    """
    return RentalRepository(test_db)


@pytest.fixture
def payment_repository(test_db):
    """
    Fixture que retorna um repositório de pagamentos com banco de teste.

    Args:
        test_db: Banco de dados de teste

    Returns:
        PaymentRepository: Repositório configurado
    """
    return PaymentRepository(test_db)


@pytest.fixture
def maintenance_repository(test_db):
    """
    Fixture que retorna um repositório de manutenções com banco de teste.

    Args:
        test_db: Banco de dados de teste

    Returns:
        MaintenanceRepository: Repositório configurado
    """
    return MaintenanceRepository(test_db)
