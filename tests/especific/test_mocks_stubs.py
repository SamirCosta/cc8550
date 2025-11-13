"""
Testes com Mocks e Stubs

Demonstra técnicas avançadas de isolamento de dependências:
- Mock de repositórios e serviços externos
- Stub de respostas de APIs e banco de dados
- Simulação de diferentes cenários (sucesso, erro, timeout)
- Verificação de chamadas e argumentos
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services import RentalService, CarService, PaymentService
from src.repositories import CarRepository
from src.utils import BusinessRuleException


class TestRepositoryMocking:
    """
    Testes que demonstram mocking de repositórios para isolar a lógica de serviço.
    """

    def test_car_service_with_mocked_repository_success(self):
        """
        Testa criação de carro com repositório mockado - cenário de sucesso.
        Demonstra: Mock básico, configuração de retorno, verificação de chamadas.
        """
        # Arrange: Criar mock do repositório
        mock_repository = Mock(spec=CarRepository)
        mock_car = Mock()
        mock_car.id = 1
        mock_car.brand = "Toyota"
        mock_car.model = "Corolla"
        mock_car.license_plate = "ABC1234"

        # Configurar comportamento do mock
        mock_repository.find_by_license_plate.return_value = None  # Placa não existe
        mock_repository.create.return_value = mock_car

        # Act: Criar serviço com repositório mockado
        car_service = CarService()
        car_service.car_repository = mock_repository

        car_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "license_plate": "ABC1234",
            "daily_rate": 150.0
        }

        result = car_service.create_car(car_data)

        # Assert: Verificar resultado e chamadas
        assert result.id == 1
        assert result.brand == "Toyota"
        mock_repository.find_by_license_plate.assert_called_once_with("ABC1234")
        mock_repository.create.assert_called_once()

    def test_rental_service_with_multiple_mocks(self):
        """
        Testa criação de aluguel com múltiplos mocks coordenados.
        Demonstra: Coordenação de múltiplos mocks, verificação de interações.
        """
        # Arrange: Criar múltiplos mocks
        rental_service = RentalService()

        # Mock do repositório de carros
        mock_car_repo = Mock(spec=CarRepository)
        mock_car = Mock()
        mock_car.id = 1
        mock_car.daily_rate = 100.0
        mock_car.is_available = True
        mock_car_repo.find_by_id.return_value = mock_car

        # Mock do customer service
        mock_customer_service = Mock()
        mock_customer_service.check_payment_status.return_value = True

        # Mock do car service
        mock_car_service = Mock()
        mock_car_service.check_availability.return_value = True

        # Mock do rental repository
        mock_rental_repo = Mock()
        mock_rental = Mock()
        mock_rental.id = 1
        mock_rental.total_value = 1000.0
        mock_rental.status = "active"
        mock_rental_repo.create.return_value = mock_rental

        # Injetar mocks
        rental_service.car_repository = mock_car_repo
        rental_service.customer_service = mock_customer_service
        rental_service.car_service = mock_car_service
        rental_service.rental_repository = mock_rental_repo

        # Act
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=10)

        rental_data = {
            "customer_id": 1,
            "car_id": 1,
            "start_date": start,
            "end_date": end
        }

        result = rental_service.create_rental(rental_data)

        # Assert: Verificar todas as interações
        assert result.id == 1
        mock_customer_service.check_payment_status.assert_called_once_with(1)
        mock_car_service.check_availability.assert_called_once_with(1)
        mock_car_repo.find_by_id.assert_called()
        mock_rental_repo.create.assert_called_once()
        mock_car_repo.update_availability.assert_called_once_with(1, False)


class TestStubbing:
    """
    Testes que demonstram uso de stubs para simular diferentes respostas.
    """

    @pytest.mark.parametrize("payment_method", [
        "credit_card",
        "debit_card",
        "pix",
        "cash",
    ])
    def test_payment_methods_with_stubs(self, payment_method):
        """
        Testa diferentes métodos de pagamento com stubs parametrizados.
        Demonstra: Stubs parametrizados, simulação de diferentes respostas.
        """
        payment_service = PaymentService()
        mock_payment_repo = Mock()

        # Stub de pagamento
        payment_stub = Mock()
        payment_stub.id = 1
        payment_stub.status = "pending"
        payment_stub.payment_method = payment_method
        payment_stub.rental_id = 1
        payment_stub.amount = 300.0
        payment_stub.payment_date = datetime.now()

        mock_payment_repo.create.return_value = payment_stub
        payment_service.payment_repository = mock_payment_repo

        # Act
        payment_data = {
            "rental_id": 1,
            "amount": 300.0,
            "payment_method": payment_method,
            "payment_date": datetime.now()
        }

        result = payment_service.create_payment(payment_data)

        # Assert
        assert result.payment_method == payment_method
        mock_payment_repo.create.assert_called_once()


class TestExternalDependencyMocking:
    """
    Testes que demonstram mocking de dependências externas (BD, APIs).
    """

    @patch('src.repositories.car_repository.CarRepository.find_by_id')
    def test_car_availability_with_patched_database(self, mock_find):
        """
        Testa verificação com banco de dados patchado usando @patch.
        Demonstra: Uso de @patch decorator, mock de dependências externas.
        """
        # Arrange: Simular resposta do banco de dados
        mock_car = Mock()
        mock_car.id = 1
        mock_car.is_available = False
        mock_find.return_value = mock_car

        car_service = CarService()

        # Mock do maintenance repository
        mock_maintenance_repo = Mock()
        mock_maintenance_repo.find_active_by_car.return_value = []
        car_service.maintenance_repository = mock_maintenance_repo

        # Act & Assert
        with pytest.raises(BusinessRuleException, match="não está disponível"):
            car_service.check_availability(1)

        mock_find.assert_called_once_with(1)


class TestErrorScenarioMocking:
    """
    Testes que simulam cenários de erro com mocks.
    """

    def test_database_connection_error_simulation(self):
        """
        Simula erro de conexão com banco de dados.
        Demonstra: Simulação de erros usando side_effect.
        """
        car_service = CarService()
        mock_car_repo = Mock()

        # Simular erro de conexão
        mock_car_repo.find_by_id.side_effect = Exception("Database connection failed")
        car_service.car_repository = mock_car_repo

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            car_service.get_car(1)

    def test_partial_failure_with_side_effects(self):
        """
        Testa falha parcial usando side_effect com lista de retornos.
        Demonstra: Múltiplos comportamentos com side_effect.
        """
        car_service = CarService()
        mock_car_repo = Mock()

        # Primeira chamada retorna carro, segunda lança exceção
        mock_car = Mock()
        mock_car.id = 1
        mock_car_repo.find_by_id.side_effect = [
            mock_car,
            Exception("Unexpected error")
        ]

        car_service.car_repository = mock_car_repo

        # Primeira chamada: sucesso
        result1 = car_service.get_car(1)
        assert result1.id == 1

        # Segunda chamada: erro
        with pytest.raises(Exception, match="Unexpected error"):
            car_service.get_car(1)
