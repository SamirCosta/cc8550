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

    Examples:
        >>> def test_car_creation(car_repository, sample_car):
        ...     created = car_repository.create(sample_car)
        ...     assert created.id is not None
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

    Examples:
        >>> def test_customer_creation(customer_repository, sample_customer):
        ...     created = customer_repository.create(sample_customer)
        ...     assert created.id is not None
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

    Examples:
        >>> def test_rental_creation(rental_repository, sample_rental):
        ...     created = rental_repository.create(sample_rental)
        ...     assert created.id is not None
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

    Examples:
        >>> def test_payment_creation(payment_repository, sample_payment):
        ...     created = payment_repository.create(sample_payment)
        ...     assert created.id is not None
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

    Examples:
        >>> def test_maintenance_creation(maintenance_repository, sample_maintenance):
        ...     created = maintenance_repository.create(sample_maintenance)
        ...     assert created.id is not None
    """
    return MaintenanceRepository(test_db)
