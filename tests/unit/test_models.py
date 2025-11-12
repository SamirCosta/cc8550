import pytest
from datetime import datetime
from src.models import Car, Customer, Rental, Payment, Maintenance

# Importar fixtures necessárias
from tests.fixtures.models import (
    sample_car,
    sample_customer,
    sample_rental,
    sample_payment,
    sample_maintenance
)


class TestCarModel:
    """
    Testes unitários para o modelo Car.
    """

    def test_car_creation(self, sample_car):
        """Testa criação de um carro."""
        assert sample_car.brand == "Toyota"
        assert sample_car.model == "Corolla"
        assert sample_car.year == 2023
        assert sample_car.license_plate == "ABC1234"
        assert sample_car.daily_rate == 150.0
        assert sample_car.is_available is True

    def test_car_to_dict(self, sample_car):
        """Testa conversão de Car para dicionário."""
        car_dict = sample_car.to_dict()
        assert car_dict["brand"] == "Toyota"
        assert car_dict["model"] == "Corolla"
        assert car_dict["year"] == 2023
        assert car_dict["license_plate"] == "ABC1234"
        assert car_dict["daily_rate"] == 150.0

    def test_car_from_dict(self):
        """Testa criação de Car a partir de dicionário."""
        data = {
            "brand": "Honda",
            "model": "Civic",
            "year": 2022,
            "license_plate": "XYZ5678",
            "daily_rate": 180.0,
            "is_available": False
        }
        car = Car.from_dict(data)
        assert car.brand == "Honda"
        assert car.model == "Civic"
        assert car.is_available is False


class TestCustomerModel:
    """
    Testes unitários para o modelo Customer.
    """

    def test_customer_creation(self, sample_customer):
        """Testa criação de um cliente."""
        assert sample_customer.name == "João Silva"
        assert sample_customer.cpf == "12345678901"
        assert sample_customer.phone == "11987654321"
        assert sample_customer.email == "joao@example.com"
        assert sample_customer.has_pending_payment is False

    def test_customer_to_dict(self, sample_customer):
        """Testa conversão de Customer para dicionário."""
        customer_dict = sample_customer.to_dict()
        assert customer_dict["name"] == "João Silva"
        assert customer_dict["cpf"] == "12345678901"
        assert customer_dict["email"] == "joao@example.com"

    def test_customer_from_dict(self):
        """Testa criação de Customer a partir de dicionário."""
        data = {
            "name": "Maria Santos",
            "cpf": "98765432100",
            "phone": "11999887766",
            "email": "maria@example.com",
            "has_pending_payment": True
        }
        customer = Customer.from_dict(data)
        assert customer.name == "Maria Santos"
        assert customer.has_pending_payment is True


class TestRentalModel:
    """
    Testes unitários para o modelo Rental.
    """

    def test_rental_creation(self, sample_rental):
        """Testa criação de um aluguel."""
        assert sample_rental.customer_id == 1
        assert sample_rental.car_id == 1
        assert sample_rental.total_value == 1500.0
        assert sample_rental.status == "active"

    def test_rental_to_dict(self, sample_rental):
        """Testa conversão de Rental para dicionário."""
        rental_dict = sample_rental.to_dict()
        assert rental_dict["customer_id"] == 1
        assert rental_dict["car_id"] == 1
        assert rental_dict["total_value"] == 1500.0
        assert rental_dict["status"] == "active"

    def test_rental_from_dict(self):
        """Testa criação de Rental a partir de dicionário."""
        data = {
            "customer_id": 2,
            "car_id": 3,
            "start_date": "2025-01-10T10:00:00",
            "end_date": "2025-01-20T10:00:00",
            "total_value": 2000.0,
            "status": "completed"
        }
        rental = Rental.from_dict(data)
        assert rental.customer_id == 2
        assert rental.car_id == 3
        assert rental.status == "completed"


class TestPaymentModel:
    """
    Testes unitários para o modelo Payment.
    """

    def test_payment_creation(self, sample_payment):
        """Testa criação de um pagamento."""
        assert sample_payment.rental_id == 1
        assert sample_payment.amount == 1500.0
        assert sample_payment.payment_method == "credit_card"
        assert sample_payment.status == "pending"

    def test_payment_to_dict(self, sample_payment):
        """Testa conversão de Payment para dicionário."""
        payment_dict = sample_payment.to_dict()
        assert payment_dict["rental_id"] == 1
        assert payment_dict["amount"] == 1500.0
        assert payment_dict["payment_method"] == "credit_card"


class TestMaintenanceModel:
    """
    Testes unitários para o modelo Maintenance.
    """

    def test_maintenance_creation(self, sample_maintenance):
        """Testa criação de uma manutenção."""
        assert sample_maintenance.car_id == 1
        assert sample_maintenance.description == "Troca de óleo"
        assert sample_maintenance.cost == 300.0
        assert sample_maintenance.status == "scheduled"

    def test_maintenance_to_dict(self, sample_maintenance):
        """Testa conversão de Maintenance para dicionário."""
        maintenance_dict = sample_maintenance.to_dict()
        assert maintenance_dict["car_id"] == 1
        assert maintenance_dict["description"] == "Troca de óleo"
        assert maintenance_dict["cost"] == 300.0
