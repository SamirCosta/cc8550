"""
Fixtures de Modelos

Fixtures que fornecem objetos de modelo de exemplo (sample data)
e objetos criados no banco de dados.
"""
import pytest
from datetime import datetime, timedelta
from src.models import Car, Customer, Rental, Payment, Maintenance
from .repositories import (
    car_repository,
    customer_repository,
    rental_repository,
    payment_repository,
    maintenance_repository
)


# ==================== Sample Data Fixtures ====================


@pytest.fixture
def sample_car():
    """
    Fixture que retorna um carro de exemplo para testes.

    Returns:
        Car: Objeto Car com dados de exemplo

    Examples:
        >>> def test_car_attributes(sample_car):
        ...     assert sample_car.brand == "Toyota"
        ...     assert sample_car.is_available is True
    """
    return Car(
        brand="Toyota",
        model="Corolla",
        year=2023,
        license_plate="ABC1234",
        daily_rate=150.0,
        is_available=True
    )


@pytest.fixture
def sample_customer():
    """
    Fixture que retorna um cliente de exemplo para testes.

    Returns:
        Customer: Objeto Customer com dados de exemplo

    Examples:
        >>> def test_customer_attributes(sample_customer):
        ...     assert sample_customer.name == "João Silva"
        ...     assert sample_customer.has_pending_payment is False
    """
    return Customer(
        name="João Silva",
        cpf="12345678901",
        phone="11987654321",
        email="joao@example.com",
        has_pending_payment=False
    )


@pytest.fixture
def sample_rental():
    """
    Fixture que retorna um aluguel de exemplo para testes.

    Returns:
        Rental: Objeto Rental com dados de exemplo

    Examples:
        >>> def test_rental_attributes(sample_rental):
        ...     assert sample_rental.status == "active"
        ...     assert sample_rental.total_value == 1500.0
    """
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=10)

    return Rental(
        customer_id=1,
        car_id=1,
        start_date=start_date,
        end_date=end_date,
        total_value=1500.0,
        status="active"
    )


@pytest.fixture
def sample_payment():
    """
    Fixture que retorna um pagamento de exemplo para testes.

    Returns:
        Payment: Objeto Payment com dados de exemplo

    Examples:
        >>> def test_payment_attributes(sample_payment):
        ...     assert sample_payment.payment_method == "credit_card"
        ...     assert sample_payment.status == "pending"
    """
    return Payment(
        rental_id=1,
        amount=1500.0,
        payment_method="credit_card",
        payment_date=datetime.now(),
        status="pending"
    )


@pytest.fixture
def sample_maintenance():
    """
    Fixture que retorna uma manutenção de exemplo para testes.

    Returns:
        Maintenance: Objeto Maintenance com dados de exemplo

    Examples:
        >>> def test_maintenance_attributes(sample_maintenance):
        ...     assert sample_maintenance.description == "Troca de óleo"
        ...     assert sample_maintenance.status == "scheduled"
    """
    return Maintenance(
        car_id=1,
        description="Troca de óleo",
        maintenance_date=datetime.now() + timedelta(days=5),
        cost=300.0,
        status="scheduled"
    )


# ==================== Created Data Fixtures ====================


@pytest.fixture
def create_test_car(car_repository, sample_car):
    """
    Fixture que cria um carro no banco de teste e retorna ele.

    Args:
        car_repository: Repositório de carros
        sample_car: Carro de exemplo

    Returns:
        Car: Carro criado no banco com ID

    Examples:
        >>> def test_with_created_car(create_test_car):
        ...     assert create_test_car.id is not None
        ...     assert create_test_car.brand == "Toyota"
    """
    return car_repository.create(sample_car)


@pytest.fixture
def create_test_customer(customer_repository, sample_customer):
    """
    Fixture que cria um cliente no banco de teste e retorna ele.

    Args:
        customer_repository: Repositório de clientes
        sample_customer: Cliente de exemplo

    Returns:
        Customer: Cliente criado no banco com ID

    Examples:
        >>> def test_with_created_customer(create_test_customer):
        ...     assert create_test_customer.id is not None
        ...     assert create_test_customer.name == "João Silva"
    """
    return customer_repository.create(sample_customer)


@pytest.fixture
def create_test_rental(rental_repository, create_test_car, create_test_customer):
    """
    Fixture que cria um aluguel no banco de teste com car e customer relacionados.

    Args:
        rental_repository: Repositório de aluguéis
        create_test_car: Carro criado no banco
        create_test_customer: Cliente criado no banco

    Returns:
        Rental: Aluguel criado no banco com IDs relacionados

    Examples:
        >>> def test_with_created_rental(create_test_rental):
        ...     assert create_test_rental.id is not None
        ...     assert create_test_rental.customer_id is not None
        ...     assert create_test_rental.car_id is not None
    """
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=10)

    rental = Rental(
        customer_id=create_test_customer.id,
        car_id=create_test_car.id,
        start_date=start_date,
        end_date=end_date,
        total_value=1500.0,
        status="active"
    )
    return rental_repository.create(rental)


@pytest.fixture
def create_test_payment(payment_repository, create_test_rental):
    """
    Fixture que cria um pagamento no banco de teste.

    Args:
        payment_repository: Repositório de pagamentos
        create_test_rental: Aluguel criado no banco

    Returns:
        Payment: Pagamento criado no banco com ID

    Examples:
        >>> def test_with_created_payment(create_test_payment):
        ...     assert create_test_payment.id is not None
        ...     assert create_test_payment.rental_id is not None
    """
    payment = Payment(
        rental_id=create_test_rental.id,
        amount=create_test_rental.total_value,
        payment_method="credit_card",
        payment_date=datetime.now(),
        status="pending"
    )
    return payment_repository.create(payment)
