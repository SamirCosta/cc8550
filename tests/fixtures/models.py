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

@pytest.fixture
def sample_car():
    """
    Fixture que retorna um carro de exemplo para testes.

    Returns:
        Car: Objeto Car com dados de exemplo
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
    """
    return Customer(
        name="João Silva",
        cpf="46627389894",
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
    """
    return Maintenance(
        car_id=1,
        description="Troca de óleo",
        maintenance_date=datetime.now() + timedelta(days=5),
        cost=300.0,
        status="scheduled"
    )


@pytest.fixture
def create_test_car(car_repository, sample_car):
    """
    Fixture que cria um carro no banco de teste e retorna ele.

    Args:
        car_repository: Repositório de carros
        sample_car: Carro de exemplo

    Returns:
        Car: Carro criado no banco com ID
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
    """
    payment = Payment(
        rental_id=create_test_rental.id,
        amount=create_test_rental.total_value,
        payment_method="credit_card",
        payment_date=datetime.now(),
        status="pending"
    )
    return payment_repository.create(payment)
