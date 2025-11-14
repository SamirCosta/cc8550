"""
Testes de mutação para RentalService.

Este módulo contém testes essenciais para detectar mutações críticas no código
do RentalService.

Categorias de mutação testadas:
1. Operadores aritméticos (*)
2. Operadores relacionais (>, >=)
3. Constantes numéricas (valores de desconto)
4. Lógica de negócio (disponibilidade, status)
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from src.services.rental_service import RentalService
from src.models import Rental, Car
from src.utils import ValidationException, BusinessRuleException


def get_future_date(days_from_now=1):
    """Retorna uma data futura para evitar validações de data passada."""
    return datetime.now() + timedelta(days=days_from_now)


class TestRentalServiceCriticalMutations:
    """Testes essenciais para detectar mutações críticas."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.rental_service = RentalService()
        self.rental_service.car_repository = Mock()
        self.rental_service.customer_repository = Mock()
        self.rental_service.rental_repository = Mock()
        self.rental_service.car_service = Mock()
        self.rental_service.customer_service = Mock()

    def test_detect_multiplication_mutation_in_base_value(self):
        """Detecta mutação: car.daily_rate * days -> car.daily_rate + days"""
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(11)  # 10 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)
        assert result == 900.0, "Mutação detectada: operador de multiplicação alterado"

    def test_detect_discount_value_mutation_20_percent(self):
        """Detecta mutação: discount = 0.20 -> discount = 0.19"""
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(32)  # 31 dias -> 20% desconto

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)
        assert result == 2480.0, "Mutação detectada: valor do desconto de 20% alterado"

    def test_detect_greater_than_mutation_in_discount_logic(self):
        """Detecta mutação: days > 30 -> days >= 30"""
        mock_car = Mock(spec=Car)
        mock_car.daily_rate = 100.0
        self.rental_service.car_repository.find_by_id.return_value = mock_car

        start_date = get_future_date(1)
        end_date = get_future_date(31)  # Exatamente 30 dias

        result = self.rental_service.calculate_rental_value(1, start_date, end_date)
        assert result == 2550.0, "Mutação detectada: condição > alterada para >="

    def test_detect_status_check_mutation_in_complete_rental(self):
        """Detecta mutação: rental.status != 'active' -> rental.status == 'active'"""
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'completed'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        with pytest.raises(BusinessRuleException, match="ativos podem ser finalizados"):
            self.rental_service.complete_rental(1)

    def test_detect_availability_mutation_in_create_rental(self):
        """Detecta mutação: update_availability(car_id, False) -> update_availability(car_id, True)"""
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
        self.rental_service.car_repository.update_availability.assert_called_once_with(1, False)

    def test_detect_status_mutation_in_complete_rental(self):
        """Detecta mutação: update_status(rental_id, 'completed') -> update_status(rental_id, 'cancelled')"""
        mock_rental = Mock(spec=Rental)
        mock_rental.status = 'active'
        mock_rental.car_id = 1
        self.rental_service.rental_repository.find_by_id.return_value = mock_rental

        self.rental_service.complete_rental(1)
        self.rental_service.rental_repository.update_status.assert_called_once_with(1, 'completed')
