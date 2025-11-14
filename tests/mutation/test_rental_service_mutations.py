"""
Testes de mutação para RentalService.

Este módulo contém testes específicos para detectar mutações no código
do RentalService, verificando se os testes conseguem identificar mudanças
em operadores, constantes, condições e lógica de negócio.

Categorias de mutação testadas:
1. Operadores aritméticos (*, -, +, /)
2. Operadores relacionais (>, <, >=, <=, ==, !=)
3. Constantes numéricas (valores de desconto, limites de dias)
4. Condições lógicas (and, or, not)
5. Valores de retorno
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from src.services.rental_service import RentalService
from src.models import Rental, Car, Customer
from src.utils import ValidationException, BusinessRuleException


def get_future_date(days_from_now=1):
    """Retorna uma data futura para evitar validações de data passada."""
    return datetime.now() + timedelta(days=days_from_now)


class TestRentalServiceArithmeticMutations:
    """Testes para detectar mutações em operadores aritméticos."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()
        self.rental_service.customer_repository = Mock()
        self.rental_service.rental_repository = Mock()
        self.rental_service.car_service = Mock()
        self.rental_service.customer_service = Mock()

    def test_detect_multiplication_mutation_in_base_value(self):
        """
        Detecta mutação: car.daily_rate * days -> car.daily_rate + days

        Se o operador de multiplicação for alterado para adição,
        o valor calculado será drasticamente diferente.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(11)  # 10 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # Com 10 dias e taxa de 100, esperamos 1000 * (1 - 0.10) = 900
        # Se fosse adição (100 + 10), seria apenas 110 * (1 - 0.10) = 99
        assert result == 900.0, "Mutação detectada: operador de multiplicação alterado"

    def test_detect_subtraction_mutation_in_days_calculation(self):
        """
        Detecta mutação: (end_date - start_date).days -> (end_date + start_date).days

        Se o operador de subtração for alterado, o cálculo de dias será incorreto.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 50.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(6)  # 5 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 5 dias * 50 = 250 (sem desconto)
        assert result == 250.0, "Mutação detectada: cálculo de dias incorreto"

    def test_detect_discount_calculation_mutation(self):
        """
        Detecta mutação: base_value * (1 - discount) -> base_value * (1 + discount)

        Se o sinal de subtração for alterado para adição no desconto,
        o valor aumentará ao invés de diminuir.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(16)  # 15 dias -> desconto de 15%

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 15 dias * 100 = 1500, com 15% desconto = 1275
        # Se fosse (1 + 0.15), seria 1725
        assert result == 1275.0, "Mutação detectada: cálculo de desconto incorreto"


class TestRentalServiceRelationalMutations:
    """Testes para detectar mutações em operadores relacionais."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()
        self.rental_service.rental_repository = Mock()

    def test_detect_greater_than_mutation_in_discount_logic(self):
        """
        Detecta mutação: days > 30 -> days >= 30

        Testa o limite exato para garantir que a condição seja precisa.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(31)  # Exatamente 30 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 30 dias deve dar 15% de desconto, não 20%
        # 30 * 100 = 3000 * 0.85 = 2550
        assert result == 2550.0, "Mutação detectada: condição > alterada para >="

    def test_detect_greater_than_or_equal_mutation_in_discount_logic(self):
        """
        Detecta mutação: days >= 15 -> days > 15

        Testa o limite de 15 dias que deve receber 15% de desconto.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(16)  # Exatamente 15 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 15 dias deve dar 15% de desconto
        # 15 * 100 = 1500 * 0.85 = 1275
        assert result == 1275.0, "Mutação detectada: condição >= alterada para >"

    def test_detect_less_than_or_equal_mutation(self):
        """
        Detecta mutação: days <= 0 -> days < 0

        Testa validação de período mínimo de aluguel.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(5)
        end_date = get_future_date(5)  # 0 dias (mesmo dia)

        with pytest.raises(ValidationException, match="pelo menos 1 dia"):
            self.rental_service.calculate_rental_value(1, start_date, end_date)


class TestRentalServiceConstantMutations:
    """Testes para detectar mutações em constantes numéricas."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()

    def test_detect_discount_value_mutation_20_percent(self):
        """
        Detecta mutação: discount = 0.20 -> discount = 0.19

        Verifica o valor exato do desconto de 20%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(32)  # 31 dias -> 20% desconto

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 31 * 100 = 3100 * 0.80 = 2480
        assert result == 2480.0, "Mutação detectada: valor do desconto de 20% alterado"

    def test_detect_discount_value_mutation_15_percent(self):
        """
        Detecta mutação: discount = 0.15 -> discount = 0.14

        Verifica o valor exato do desconto de 15%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(16)  # 15 dias -> 15% desconto

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 15 * 100 = 1500 * 0.85 = 1275
        assert result == 1275.0, "Mutação detectada: valor do desconto de 15% alterado"

    def test_detect_discount_value_mutation_10_percent(self):
        """
        Detecta mutação: discount = 0.10 -> discount = 0.09

        Verifica o valor exato do desconto de 10%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(9)  # 8 dias -> 10% desconto

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 8 * 100 = 800 * 0.90 = 720
        assert result == 720.0, "Mutação detectada: valor do desconto de 10% alterado"

    def test_detect_day_threshold_mutation_30_days(self):
        """
        Detecta mutação: days > 30 -> days > 31

        Verifica o limite exato de 31 dias para desconto de 20%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(32)  # 31 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 31 dias deve dar 20% de desconto
        assert result == 2480.0, "Mutação detectada: limite de dias alterado"

    def test_detect_day_threshold_mutation_15_days(self):
        """
        Detecta mutação: days >= 15 -> days >= 16

        Verifica o limite exato de 15 dias para desconto de 15%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(16)  # 15 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 15 dias deve dar 15% de desconto
        assert result == 1275.0, "Mutação detectada: limite de dias alterado"

    def test_detect_day_threshold_mutation_8_days(self):
        """
        Detecta mutação: days >= 8 -> days >= 9

        Verifica o limite exato de 8 dias para desconto de 10%.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(9)  # 8 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)

        # 8 dias deve dar 10% de desconto
        assert result == 720.0, "Mutação detectada: limite de dias alterado"


class TestRentalServiceConditionalMutations:
    """Testes para detectar mutações em condições lógicas."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()
        self.rental_service.customer_repository = Mock()
        self.rental_service.rental_repository = Mock()
        self.rental_service.car_service = Mock()
        self.rental_service.customer_service = Mock()

    def test_detect_status_check_mutation_in_complete_rental(self):
        """
        Detecta mutação: rental.status != 'active' -> rental.status == 'active'

        Garante que apenas aluguéis ativos possam ser finalizados.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'completed'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        with pytest.raises(BusinessRuleException, match="ativos podem ser finalizados"):
            self.rental_service.complete_rental(1)

    def test_detect_status_check_mutation_in_cancel_rental(self):
        """
        Detecta mutação: rental.status != 'active' -> rental.status == 'active'

        Garante que apenas aluguéis ativos possam ser cancelados.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'cancelled'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        with pytest.raises(BusinessRuleException, match="ativos podem ser cancelados"):
            self.rental_service.cancel_rental(1)


class TestRentalServiceBusinessLogicMutations:
    """Testes para detectar mutações em lógica de negócio."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()
        self.rental_service.customer_repository = Mock()
        self.rental_service.rental_repository = Mock()
        self.rental_service.car_service = Mock()
        self.rental_service.customer_service = Mock()

    def test_detect_availability_mutation_in_create_rental(self):
        """
        Detecta mutação: update_availability(car_id, False) -> update_availability(car_id, True)

        Garante que o carro seja marcado como indisponível ao criar aluguel.
        """
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        mock_rental = Mock(spec=Rental)
        mock_rental.id = 1
        self.rental_service.rental_repository.create.return_value = mock_rental

        rental_data = {
            'customer_id': 1,
            'car_id': 1,
            'start_date': get_future_date(1),
            'end_date': get_future_date(5)
        }

        self.rental_service.create_rental(rental_data)

        # Verifica se foi chamado com False (indisponível)
        self.rental_service.car_repository.update_availability.assert_called_once_with(1, False)

    def test_detect_availability_mutation_in_complete_rental(self):
        """
        Detecta mutação: update_availability(car_id, True) -> update_availability(car_id, False)

        Garante que o carro seja marcado como disponível ao finalizar aluguel.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'active'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        self.rental_service.complete_rental(1)

        # Verifica se foi chamado com True (disponível)
        self.rental_service.car_repository.update_availability.assert_called_once_with(1, True)

    def test_detect_status_mutation_in_complete_rental(self):
        """
        Detecta mutação: update_status(rental_id, 'completed') -> update_status(rental_id, 'cancelled')

        Garante que o status seja atualizado corretamente ao finalizar.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'active'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        self.rental_service.complete_rental(1)

        # Verifica se foi chamado com 'completed'
        self.rental_service.rental_repository.update_status.assert_called_once_with(1, 'completed')

    def test_detect_status_mutation_in_cancel_rental(self):
        """
        Detecta mutação: update_status(rental_id, 'cancelled') -> update_status(rental_id, 'completed')

        Garante que o status seja atualizado corretamente ao cancelar.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'active'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        self.rental_service.cancel_rental(1)

        # Verifica se foi chamado com 'cancelled'
        self.rental_service.rental_repository.update_status.assert_called_once_with(1, 'cancelled')
