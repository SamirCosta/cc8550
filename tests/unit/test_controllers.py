"""
Testes Unitários para Controllers

Este módulo contém testes unitários para todos os controllers da aplicação.
Os testes usam mocks para isolar a lógica de cada controller.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from src.models import Car, Customer, Rental, Payment, Maintenance
from src.utils import (
    NotFoundException,
    ValidationException,
    BusinessRuleException,
    RentalException
)

class TestCarController:
    """Testes para o CarController"""

    @patch('src.controllers.car_controller.car_service')
    def test_create_car_success(self, mock_service):
        """Testa criação de carro com sucesso"""
        from src.controllers.car_controller import create_car, CarCreate

        car_data = CarCreate(
            brand="Toyota", model="Corolla", year=2023,
            license_plate="ABC1D23", daily_rate=150.0
        )
        mock_car = Car(id=1, brand="Toyota", model="Corolla", year=2023,
                      license_plate="ABC1D23", daily_rate=150.0, is_available=True)
        mock_service.create_car.return_value = mock_car

        result = create_car(car_data)

        assert result['id'] == 1
        assert result['brand'] == "Toyota"

    @patch('src.controllers.car_controller.car_service')
    def test_get_car_not_found(self, mock_service):
        """Testa busca de carro não encontrado"""
        from src.controllers.car_controller import get_car

        mock_service.get_car.side_effect = NotFoundException("Car not found")

        with pytest.raises(HTTPException) as exc_info:
            get_car(999)
        assert exc_info.value.status_code == 404

    @patch('src.controllers.car_controller.car_service')
    def test_search_available_cars_success(self, mock_service):
        """Testa busca de carros disponíveis"""
        from src.controllers.car_controller import search_available_cars

        mock_cars = [
            Car(id=1, brand="Toyota", model="Corolla", year=2023,
                license_plate="ABC1D23", daily_rate=150.0, is_available=True)
        ]
        mock_service.get_available_cars.return_value = mock_cars

        result = search_available_cars(brand="Toyota")

        assert len(result) == 1
        assert result[0]['brand'] == "Toyota"


class TestCustomerController:
    """Testes para o CustomerController"""

    @patch('src.controllers.customer_controller.customer_service')
    def test_create_customer_success(self, mock_service):
        """Testa criação de cliente com sucesso"""
        from src.controllers.customer_controller import create_customer, CustomerCreate

        customer_data = CustomerCreate(
            name="João Silva", cpf="12345678900", phone="11999887766",
            email="joao@example.com", has_pending_payment=False
        )
        mock_customer = Customer(
            id=1, name="João Silva", cpf="12345678900", phone="11999887766",
            email="joao@example.com", has_pending_payment=False
        )
        mock_service.create_customer.return_value = mock_customer

        result = create_customer(customer_data)

        assert result['id'] == 1
        assert result['name'] == "João Silva"

    @patch('src.controllers.customer_controller.customer_service')
    def test_get_customer_not_found(self, mock_service):
        """Testa busca de cliente não encontrado"""
        from src.controllers.customer_controller import get_customer

        mock_service.get_customer.side_effect = NotFoundException("Customer not found")

        with pytest.raises(HTTPException) as exc_info:
            get_customer(999)
        assert exc_info.value.status_code == 404


class TestRentalController:
    """Testes para o RentalController"""

    @patch('src.controllers.rental_controller.rental_service')
    def test_create_rental_success(self, mock_service):
        """Testa criação de aluguel com sucesso"""
        from src.controllers.rental_controller import create_rental, RentalCreate

        rental_data = RentalCreate(
            customer_id=1, car_id=1,
            start_date="2024-01-01", end_date="2024-01-10"
        )
        mock_rental = Rental(
            id=1, customer_id=1, car_id=1,
            start_date="2024-01-01", end_date="2024-01-10",
            total_value=1350.0, status="active"
        )
        mock_service.create_rental.return_value = mock_rental

        result = create_rental(rental_data)

        assert result['id'] == 1
        assert result['total_value'] == 1350.0

    @patch('src.controllers.rental_controller.rental_service')
    def test_get_rental_not_found(self, mock_service):
        """Testa busca de aluguel não encontrado"""
        from src.controllers.rental_controller import get_rental

        mock_service.get_rental.side_effect = NotFoundException("Rental not found")

        with pytest.raises(HTTPException) as exc_info:
            get_rental(999)
        assert exc_info.value.status_code == 404

    @patch('src.controllers.rental_controller.rental_service')
    def test_search_rentals_with_filters(self, mock_service):
        """Testa busca de aluguéis com filtros"""
        from src.controllers.rental_controller import search_rentals

        mock_rentals = [
            Rental(id=1, customer_id=1, car_id=1,
                  start_date="2024-01-01", end_date="2024-01-10",
                  total_value=1350.0, status="active")
        ]
        mock_service.search_rentals.return_value = mock_rentals

        result = search_rentals(customer_id=1, status="active")

        assert len(result) == 1
        assert result[0]['status'] == "active"


class TestPaymentController:
    """Testes para o PaymentController"""

    @patch('src.controllers.payment_controller.payment_service')
    def test_create_payment_success(self, mock_service):
        """Testa criação de pagamento com sucesso"""
        from src.controllers.payment_controller import create_payment, PaymentCreate

        payment_data = PaymentCreate(
            rental_id=1, amount=1350.0, payment_method="credit_card",
            payment_date="2024-01-10", status="pending"
        )
        mock_payment = Payment(
            id=1, rental_id=1, amount=1350.0, payment_method="credit_card",
            payment_date="2024-01-10", status="pending"
        )
        mock_service.create_payment.return_value = mock_payment

        result = create_payment(payment_data)

        assert result['id'] == 1
        assert result['amount'] == 1350.0

    @patch('src.controllers.payment_controller.payment_service')
    def test_get_payment_not_found(self, mock_service):
        """Testa busca de pagamento não encontrado"""
        from src.controllers.payment_controller import get_payment

        mock_service.get_payment.side_effect = NotFoundException("Payment not found")

        with pytest.raises(HTTPException) as exc_info:
            get_payment(999)
        assert exc_info.value.status_code == 404

    @patch('src.controllers.payment_controller.payment_service')
    def test_get_payments_by_rental_success(self, mock_service):
        """Testa busca de pagamentos por aluguel"""
        from src.controllers.payment_controller import get_payments_by_rental

        mock_payments = [
            Payment(id=1, rental_id=1, amount=1350.0, payment_method="credit_card",
                   payment_date="2024-01-10", status="paid")
        ]
        mock_service.get_payments_by_rental.return_value = mock_payments

        result = get_payments_by_rental(1)

        assert len(result) == 1
        assert result[0]['rental_id'] == 1


class TestMaintenanceController:
    """Testes para o MaintenanceController"""

    @patch('src.controllers.maintenance_controller.maintenance_service')
    def test_create_maintenance_success(self, mock_service):
        """Testa criação de manutenção com sucesso"""
        from src.controllers.maintenance_controller import create_maintenance, MaintenanceCreate

        maintenance_data = MaintenanceCreate(
            car_id=1, description="Troca de óleo",
            maintenance_date="2024-01-15", cost=150.0, status="scheduled"
        )
        mock_maintenance = Maintenance(
            id=1, car_id=1, description="Troca de óleo",
            maintenance_date="2024-01-15", cost=150.0, status="scheduled"
        )
        mock_service.create_maintenance.return_value = mock_maintenance

        result = create_maintenance(maintenance_data)

        assert result['id'] == 1
        assert result['description'] == "Troca de óleo"

    @patch('src.controllers.maintenance_controller.maintenance_service')
    def test_get_maintenance_not_found(self, mock_service):
        """Testa busca de manutenção não encontrada"""
        from src.controllers.maintenance_controller import get_maintenance

        mock_service.get_maintenance.side_effect = NotFoundException("Maintenance not found")

        with pytest.raises(HTTPException) as exc_info:
            get_maintenance(999)
        assert exc_info.value.status_code == 404

    @patch('src.controllers.maintenance_controller.maintenance_service')
    def test_get_maintenances_by_car_success(self, mock_service):
        """Testa busca de manutenções por carro"""
        from src.controllers.maintenance_controller import get_maintenances_by_car

        mock_maintenances = [
            Maintenance(id=1, car_id=1, description="Troca de óleo",
                       maintenance_date="2024-01-15", cost=150.0, status="completed")
        ]
        mock_service.get_maintenances_by_car.return_value = mock_maintenances

        result = get_maintenances_by_car(1)

        assert len(result) == 1
        assert result[0]['car_id'] == 1
