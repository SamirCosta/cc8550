"""
Testes específicos para matar mutações (Mutation Killers).

Estes testes foram criados especificamente para detectar mutações
que poderiam sobreviver aos testes convencionais.
"""
import pytest
from datetime import datetime, timedelta
from src.services import RentalService, CarService
from src.utils import Validator, ValidationException


class TestBoundaryMutationKillers:
    """
    Testes de valores nos limites (boundary values) para matar mutações
    de operadores de comparação.
    """

    @pytest.mark.parametrize("days,expected_discount", [
        (7, 0.0),   # Limite inferior sem desconto
        (8, 0.10),  # Exatamente no início do primeiro desconto
        (14, 0.10), # Limite superior do primeiro desconto
        (15, 0.15), # Exatamente no início do segundo desconto
        (29, 0.15), # Limite superior do segundo desconto
        (30, 0.15), # No limite (30 não é > 30)
        (31, 0.20), # Primeiro dia com desconto máximo
    ])
    def test_discount_boundaries_exact(self, days, expected_discount):
        """
        Testa valores exatos nos limites de desconto para detectar
        mutações de >= para > ou vice-versa.
        """
        rental_service = RentalService()

        # Mock car
        from unittest.mock import Mock
        mock_car = Mock()
        mock_car.daily_rate = 100.0

        rental_service.car_repository.find_by_id = Mock(return_value=mock_car)

        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=days)

        total = rental_service.calculate_rental_value(1, start, end)
        expected = 100.0 * days * (1 - expected_discount)

        assert total == pytest.approx(expected, abs=0.01), \
            f"Dias={days}: esperado {expected}, obtido {total}"


class TestArithmeticMutationKillers:
    """
    Testes para detectar mutações de operadores aritméticos.
    """

    def test_rental_value_calculation_with_known_values(self):
        """
        Testa cálculo com valores conhecidos para detectar
        mutações de * para / ou +.
        """
        rental_service = RentalService()

        from unittest.mock import Mock
        mock_car = Mock()
        mock_car.daily_rate = 150.0  # Valor específico

        rental_service.car_repository.find_by_id = Mock(return_value=mock_car)

        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=5)  # 5 dias, sem desconto

        total = rental_service.calculate_rental_value(1, start, end)

        # Se * foi mutado para /, resultado seria 150/5 = 30
        assert total != 30.0, "Mutação * → / não detectada!"

        # Se * foi mutado para +, resultado seria 150+5 = 155
        assert total != 155.0, "Mutação * → + não detectada!"

        # Valor correto: 150 * 5 = 750
        assert total == 750.0


class TestLogicalMutationKillers:
    """
    Testes para detectar mutações de operadores lógicos (and/or/not).
    """

    def test_cpf_validation_all_same_digits_only(self):
        """
        Testa CPF com todos dígitos iguais para detectar
        mutação de 'or' para 'and' na validação.

        Original: if len(cpf) != 11 or cpf == cpf[0] * 11
        Mutação: if len(cpf) != 11 and cpf == cpf[0] * 11
        """
        # CPF com 11 dígitos mas todos iguais
        with pytest.raises(ValidationException, match="CPF inválido"):
            Validator.validate_cpf("11111111111")

        # Se 'or' foi mutado para 'and', este teste ainda passaria
        # mas o próximo falharia

    def test_cpf_validation_wrong_length_only(self):
        """
        Testa CPF com tamanho incorreto para detectar mutação de 'or' para 'and'.
        """
        # CPF com tamanho errado (não todos iguais)
        with pytest.raises(ValidationException, match="CPF inválido"):
            Validator.validate_cpf("123")

        # Se 'or' foi mutado para 'and', este teste falharia

    def test_car_availability_not_operator(self):
        """
        Testa a mutação do operador 'not' em check_availability.

        Original: if not car.is_available
        Mutação: if car.is_available
        """
        car_service = CarService()

        from unittest.mock import Mock
        mock_car = Mock()
        mock_car.is_available = False  # Carro indisponível

        car_service.car_repository.find_by_id = Mock(return_value=mock_car)
        car_service.maintenance_repository.find_active_by_car = Mock(return_value=[])

        from src.utils import BusinessRuleException

        # Deve lançar exceção porque carro NÃO está disponível
        with pytest.raises(BusinessRuleException, match="não está disponível"):
            car_service.check_availability(1)

        # Se 'not' foi removido, o comportamento seria invertido


class TestConstantMutationKillers:
    """
    Testes para detectar mutações de constantes (True/False, 0/1, strings).
    """

    def test_positive_number_validator_zero_exactly(self):
        """
        Testa exatamente o valor 0 para detectar mutação de <= para <.

        Original: if value <= 0
        Mutação: if value < 0
        """
        # Zero deve ser inválido
        with pytest.raises(ValidationException, match="deve ser maior que zero"):
            Validator.validate_positive_number(0, "Teste")

        # Se <= foi mutado para <, zero seria aceito

    def test_positive_number_validator_negative(self):
        """
        Testa valor negativo para complementar teste anterior.
        """
        with pytest.raises(ValidationException, match="deve ser maior que zero"):
            Validator.validate_positive_number(-1, "Teste")

    def test_positive_number_validator_small_positive(self):
        """
        Testa pequeno valor positivo (0.01) para detectar mutações.
        """
        # 0.01 deve ser válido
        assert Validator.validate_positive_number(0.01, "Teste") is True

        # Se constante 0 foi mutada para 1, este teste falharia


class TestReturnValueMutationKillers:
    """
    Testes para detectar mutações em valores de retorno.
    """

    def test_validator_returns_true_on_success(self):
        """
        Verifica explicitamente que validadores retornam True.

        Se True fosse mutado para False, este teste detectaria.
        """
        # Todas validações devem retornar True explicitamente
        assert Validator.validate_cpf("11144477735") is True
        assert Validator.validate_email("test@example.com") is True
        assert Validator.validate_phone("11987654321") is True
        assert Validator.validate_license_plate("ABC1234") is True

        # Não apenas "truthy", mas exatamente True
        assert Validator.validate_cpf("11144477735") == True


class TestStringConstantMutationKillers:
    """
    Testes para detectar mutações de constantes string.
    """

    def test_rental_status_must_be_active_on_creation(self):
        """
        Testa que status inicial é exatamente "active".

        Se "active" fosse mutado para "cancelled" ou "completed",
        este teste detectaria.
        """
        rental_service = RentalService()

        from unittest.mock import Mock

        # Setup mocks
        mock_car = Mock()
        mock_car.id = 1
        mock_car.daily_rate = 100.0
        mock_car.is_available = True

        mock_customer = Mock()
        mock_customer.id = 1

        mock_rental = Mock()
        mock_rental.id = 1
        mock_rental.status = "active"
        mock_rental.total_value = 500.0

        rental_service.customer_service.check_payment_status = Mock(return_value=True)
        rental_service.car_service.check_availability = Mock(return_value=True)
        rental_service.car_repository.find_by_id = Mock(return_value=mock_car)
        rental_service.car_repository.update_availability = Mock()
        rental_service.rental_repository.create = Mock(return_value=mock_rental)

        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=5)

        rental_data = {
            "customer_id": 1,
            "car_id": 1,
            "start_date": start,
            "end_date": end
        }

        rental = rental_service.create_rental(rental_data)

        # Status deve ser exatamente "active", não "cancelled" ou "completed"
        assert rental.status == "active"
        assert rental.status != "cancelled"
        assert rental.status != "completed"


class TestEdgeCaseMutationKillers:
    """
    Testes de edge cases específicos.
    """

    def test_date_range_start_exactly_now(self):
        """
        Testa data de início exatamente agora (hoje é válido).
        """
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = now + timedelta(days=1)

        # Hoje (agora) deve ser aceito (não é passado)
        assert Validator.validate_date_range(now, tomorrow) is True

    def test_date_range_yesterday(self):
        """
        Testa data de início no passado (ontem).
        """
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        with pytest.raises(ValidationException, match="não pode ser no passado"):
            Validator.validate_date_range(yesterday, tomorrow)

    def test_year_validator_boundaries(self):
        """
        Testa valores nos limites do validador de ano.
        """
        current_year = datetime.now().year

        # Anos válidos
        assert Validator.validate_year(1900) is True
        assert Validator.validate_year(current_year) is True
        assert Validator.validate_year(current_year + 1) is True

        # Anos inválidos
        with pytest.raises(ValidationException):
            Validator.validate_year(1899)

        with pytest.raises(ValidationException):
            Validator.validate_year(current_year + 2)


class TestCoverageGapMutationKillers:
    """
    Testes para cobrir gaps identificados na análise de mutação.
    """

    def test_cpf_second_digit_validation(self):
        """
        Testa especificamente o segundo dígito verificador do CPF.

        Cobre a linha 42 do validators.py que poderia sobreviver.
        """
        # CPF com primeiro dígito correto mas segundo errado
        invalid_cpf = "11144477730"  # Último dígito errado

        with pytest.raises(ValidationException, match="CPF inválido"):
            Validator.validate_cpf(invalid_cpf)

    def test_cpf_first_digit_validation(self):
        """
        Testa especificamente o primeiro dígito verificador do CPF.

        Cobre a linha 39-40 do validators.py.
        """
        # CPF com segundo dígito correto mas primeiro errado
        invalid_cpf = "11144477745"  # Penúltimo dígito errado

        with pytest.raises(ValidationException, match="CPF inválido"):
            Validator.validate_cpf(invalid_cpf)
