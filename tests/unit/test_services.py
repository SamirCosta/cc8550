import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from src.services import CarService, CustomerService, RentalService, PaymentService
from src.utils import ValidationException, BusinessRuleException, NotFoundException


class TestCarService:
    """
    Testes unitários para CarService com mocks.
    """

    def test_create_car_success(self):
        """Testa criação de carro com sucesso."""
        mock_repo = Mock()
        mock_repo.find_by_license_plate.return_value = None
        mock_repo.create.return_value = Mock(id=1, brand="Toyota", daily_rate=150.0)

        service = CarService(car_repository=mock_repo)
        car_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "license_plate": "ABC1234",
            "daily_rate": 150.0
        }

        result = service.create_car(car_data)
        assert result.id == 1
        mock_repo.find_by_license_plate.assert_called_once()
        mock_repo.create.assert_called_once()

    def test_create_car_duplicate_plate(self):
        """Testa tentativa de criar carro com placa duplicada."""
        mock_repo = Mock()
        mock_repo.find_by_license_plate.return_value = Mock(id=1)

        service = CarService(car_repository=mock_repo)
        car_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "license_plate": "ABC1234",
            "daily_rate": 150.0
        }

        with pytest.raises(BusinessRuleException, match="Placa já cadastrada"):
            service.create_car(car_data)

    def test_check_availability_success(self):
        """Testa verificação de disponibilidade com carro disponível."""
        mock_car_repo = Mock()
        mock_maintenance_repo = Mock()

        mock_car_repo.find_by_id.return_value = Mock(id=1, is_available=True)
        mock_maintenance_repo.find_active_by_car.return_value = []

        service = CarService(
            car_repository=mock_car_repo,
            maintenance_repository=mock_maintenance_repo
        )

        result = service.check_availability(1)
        assert result is True

    def test_check_availability_car_unavailable(self):
        """Testa verificação de disponibilidade com carro indisponível."""
        mock_car_repo = Mock()
        mock_car_repo.find_by_id.return_value = Mock(id=1, is_available=False)

        service = CarService(car_repository=mock_car_repo)

        with pytest.raises(BusinessRuleException, match="não está disponível"):
            service.check_availability(1)

    def test_check_availability_with_active_maintenance(self):
        """Testa verificação de disponibilidade com manutenção ativa."""
        mock_car_repo = Mock()
        mock_maintenance_repo = Mock()

        mock_car_repo.find_by_id.return_value = Mock(id=1, is_available=True)
        mock_maintenance_repo.find_active_by_car.return_value = [Mock(id=1)]

        service = CarService(
            car_repository=mock_car_repo,
            maintenance_repository=mock_maintenance_repo
        )

        with pytest.raises(BusinessRuleException, match="manutenção ativa"):
            service.check_availability(1)


class TestCustomerService:
    """
    Testes unitários para CustomerService com mocks.
    """

    def test_create_customer_success(self):
        """Testa criação de cliente com sucesso."""
        mock_repo = Mock()
        mock_repo.find_by_cpf.return_value = None
        mock_repo.find_by_email.return_value = None
        mock_repo.create.return_value = Mock(id=1, name="João")

        service = CustomerService(customer_repository=mock_repo)
        customer_data = {
            "name": "João Silva",
            "cpf": "11144477735",
            "phone": "11987654321",
            "email": "joao@example.com"
        }

        result = service.create_customer(customer_data)
        assert result.id == 1
        mock_repo.create.assert_called_once()

    def test_create_customer_duplicate_cpf(self):
        """Testa tentativa de criar cliente com CPF duplicado."""
        mock_repo = Mock()
        mock_repo.find_by_cpf.return_value = Mock(id=1)

        service = CustomerService(customer_repository=mock_repo)
        customer_data = {
            "name": "João Silva",
            "cpf": "11144477735",
            "phone": "11987654321",
            "email": "joao@example.com"
        }

        with pytest.raises(BusinessRuleException, match="CPF já cadastrado"):
            service.create_customer(customer_data)

    def test_check_payment_status_no_pending(self):
        """Testa verificação de status sem pagamentos pendentes."""
        mock_customer_repo = Mock()
        mock_payment_repo = Mock()
        mock_rental_repo = Mock()

        mock_rental_repo.find_by_customer.return_value = []

        service = CustomerService(
            customer_repository=mock_customer_repo,
            payment_repository=mock_payment_repo,
            rental_repository=mock_rental_repo
        )

        result = service.check_payment_status(1)
        assert result is True

    def test_check_payment_status_with_pending(self):
        """Testa verificação de status com pagamento pendente."""
        mock_customer_repo = Mock()
        mock_payment_repo = Mock()
        mock_rental_repo = Mock()

        mock_rental_repo.find_by_customer.return_value = [Mock(id=1)]
        mock_payment_repo.find_pending_by_rental.return_value = [Mock(id=1)]

        service = CustomerService(
            customer_repository=mock_customer_repo,
            payment_repository=mock_payment_repo,
            rental_repository=mock_rental_repo
        )

        with pytest.raises(BusinessRuleException, match="pagamento pendente"):
            service.check_payment_status(1)


class TestRentalService:
    """
    Testes unitários para RentalService com testes de regras de negócio.
    """

    @pytest.mark.parametrize("days,expected_discount", [
        (5, 0.0),
        (10, 0.10),
        (20, 0.15),
        (35, 0.20)
    ])
    def test_calculate_rental_value_discounts(self, days, expected_discount):
        """Testa cálculo de valor com diferentes períodos e descontos."""
        mock_car_repo = Mock()
        mock_car_repo.find_by_id.return_value = Mock(daily_rate=100.0)

        service = RentalService(car_repository=mock_car_repo)

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=days)

        value = service.calculate_rental_value(1, start_date, end_date)

        expected_value = 100.0 * days * (1 - expected_discount)
        assert value == pytest.approx(expected_value, rel=0.01)

    def test_create_rental_success(self):
        """Testa criação de aluguel com todas as validações."""
        mock_rental_repo = Mock()
        mock_car_repo = Mock()
        mock_customer_repo = Mock()
        mock_car_service = Mock()
        mock_customer_service = Mock()

        mock_car_repo.find_by_id.return_value = Mock(daily_rate=150.0)
        mock_car_service.check_payment_status.return_value = True
        mock_car_service.check_availability.return_value = True
        mock_rental_repo.create.return_value = Mock(id=1, total_value=1500.0)

        service = RentalService(
            rental_repository=mock_rental_repo,
            car_repository=mock_car_repo,
            customer_repository=mock_customer_repo,
            car_service=mock_car_service,
            customer_service=mock_customer_service
        )

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=10)

        rental_data = {
            "customer_id": 1,
            "car_id": 1,
            "start_date": start_date,
            "end_date": end_date
        }

        result = service.create_rental(rental_data)
        assert result.id == 1
        mock_car_repo.update_availability.assert_called_once_with(1, False)

    def test_complete_rental_success(self):
        """Testa finalização de aluguel."""
        mock_rental_repo = Mock()
        mock_car_repo = Mock()

        mock_rental_repo.find_by_id.return_value = Mock(id=1, status="active", car_id=1)

        service = RentalService(
            rental_repository=mock_rental_repo,
            car_repository=mock_car_repo
        )

        service.complete_rental(1)

        mock_rental_repo.update_status.assert_called_once_with(1, "completed")
        mock_car_repo.update_availability.assert_called_once_with(1, True)

    def test_complete_rental_invalid_status(self):
        """Testa tentativa de finalizar aluguel já finalizado."""
        mock_rental_repo = Mock()
        mock_rental_repo.find_by_id.return_value = Mock(id=1, status="completed")

        service = RentalService(rental_repository=mock_rental_repo)

        with pytest.raises(BusinessRuleException, match="Apenas aluguéis ativos"):
            service.complete_rental(1)


class TestPaymentService:
    """
    Testes unitários para PaymentService.
    """

    @pytest.mark.parametrize("method", [
        "credit_card",
        "debit_card",
        "cash",
        "pix"
    ])
    def test_create_payment_valid_methods(self, method):
        """Testa criação de pagamento com métodos válidos."""
        mock_payment_repo = Mock()
        mock_rental_repo = Mock()

        mock_rental_repo.find_by_id.return_value = Mock(id=1, customer_id=1)
        mock_payment_repo.create.return_value = Mock(id=1, status="pending")

        service = PaymentService(
            payment_repository=mock_payment_repo,
            rental_repository=mock_rental_repo
        )

        payment_data = {
            "rental_id": 1,
            "amount": 1500.0,
            "payment_method": method,
            "payment_date": datetime.now()
        }

        result = service.create_payment(payment_data)
        assert result.id == 1

    def test_create_payment_invalid_method(self):
        """Testa criação de pagamento com método inválido."""
        mock_rental_repo = Mock()
        mock_rental_repo.find_by_id.return_value = Mock(id=1)

        service = PaymentService(rental_repository=mock_rental_repo)

        payment_data = {
            "rental_id": 1,
            "amount": 1500.0,
            "payment_method": "invalid_method",
            "payment_date": datetime.now()
        }

        with pytest.raises(ValidationException, match="Método de pagamento inválido"):
            service.create_payment(payment_data)

    def test_process_payment_success(self):
        """Testa processamento de pagamento pendente."""
        mock_payment_repo = Mock()
        mock_rental_repo = Mock()
        mock_customer_repo = Mock()

        mock_payment_repo.find_by_id.side_effect = [
            Mock(id=1, status="pending", rental_id=1),
            Mock(id=1, status="completed", rental_id=1)
        ]
        mock_rental_repo.find_by_id.return_value = Mock(customer_id=1)
        mock_rental_repo.find_by_customer.return_value = []

        service = PaymentService(
            payment_repository=mock_payment_repo,
            rental_repository=mock_rental_repo,
            customer_repository=mock_customer_repo
        )

        result = service.process_payment(1)
        assert result.status == "completed"
        mock_payment_repo.update_status.assert_called_once_with(1, "completed")
