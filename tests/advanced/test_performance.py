"""
Testes de Performance e Carga

Demonstra técnicas de teste de performance:
- Medição de tempo de execução (pytest-benchmark)
- Testes com grandes volumes de dados
- Identificação de gargalos de performance
- Comparação de diferentes implementações
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
import time

from src.services import RentalService
from src.utils import Validator
from src.models import Car, Customer


class TestBasicPerformance:
    """
    Testes básicos de performance para operações críticas.
    """

    def test_cpf_validation_performance(self, benchmark):
        """
        Mede performance da validação de CPF.
        Demonstra: Benchmark básico com pytest-benchmark.
        """
        valid_cpf = "11144477735"
        result = benchmark(Validator.validate_cpf, valid_cpf)
        assert result is True

    def test_rental_calculation_performance(self, benchmark):
        """
        Mede performance do cálculo de valor de aluguel.
        Demonstra: Benchmark de operação de negócio complexa.
        """
        rental_service = RentalService()

        # Mock do repositório
        mock_car = Mock()
        mock_car.daily_rate = 100.0
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = mock_car
        rental_service.car_repository = mock_repo

        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=10)

        result = benchmark(rental_service.calculate_rental_value, 1, start, end)
        assert result > 0


class TestBulkOperationsPerformance:
    """
    Testes de performance com operações em lote.
    """

    def test_bulk_cpf_validation(self, benchmark):
        """
        Testa validação de múltiplos CPFs para medir throughput.
        Demonstra: Performance de operações em lote (100 validações).
        """
        valid_cpfs = [
            "11144477735",
            "52998224725",
            "84434916041",
            "11144477735",
            "52998224725",
        ] * 20  # 100 CPFs

        def validate_all():
            return [Validator.validate_cpf(cpf) for cpf in valid_cpfs]

        result = benchmark(validate_all)
        assert len(result) == 100
        assert all(result)

    def test_model_creation_performance(self, benchmark):
        """
        Mede performance de criação de múltiplos modelos.
        Demonstra: Performance de instanciação de objetos.
        """
        def create_multiple_cars():
            cars = []
            for i in range(100):
                car = Car(
                    id=i,
                    brand=f"Brand{i}",
                    model=f"Model{i}",
                    year=2020 + (i % 5),
                    license_plate=f"ABC{i:04d}",
                    daily_rate=100.0 + i,
                    is_available=True
                )
                cars.append(car)
            return cars

        result = benchmark(create_multiple_cars)
        assert len(result) == 100


class TestLargeDatasetPerformance:
    """
    Testes com grandes volumes de dados.
    """

    def test_validation_with_large_dataset(self, benchmark):
        """
        Testa validação com grande conjunto de dados (1000 validações).
        Demonstra: Comportamento com grande volume de dados.
        """
        base_cpfs = [
            "11144477735",
            "52998224725",
            "84434916041",
        ]
        large_cpf_list = base_cpfs * 334  # ~1000 CPFs

        def validate_large_dataset():
            valid_count = 0
            for cpf in large_cpf_list:
                if Validator.validate_cpf(cpf):
                    valid_count += 1
            return valid_count

        result = benchmark(validate_large_dataset)
        assert result > 0

    def test_model_serialization_performance(self, benchmark):
        """
        Testa performance de serialização de modelos (500 objetos).
        Demonstra: Performance de conversão de objetos para dicionário.
        """
        customers = []
        for i in range(500):
            customer = Customer(
                id=i,
                name=f"Customer {i}",
                cpf=f"{i:011d}",
                phone="11987654321",
                email=f"customer{i}@example.com",
                has_pending_payment=False
            )
            customers.append(customer)

        def serialize_all():
            return [customer.to_dict() for customer in customers]

        result = benchmark(serialize_all)
        assert len(result) == 500


class TestTimingConstraints:
    """
    Testes que verificam restrições de tempo (SLA).
    """

    def test_cpf_validation_meets_timing_requirement(self):
        """
        Verifica que validação de CPF leva menos de 1ms.
        Demonstra: Validação de SLA de performance.
        """
        cpf = "11144477735"

        start = time.perf_counter()
        for _ in range(1000):
            Validator.validate_cpf(cpf)
        end = time.perf_counter()

        avg_time = (end - start) / 1000
        assert avg_time < 0.001, f"Validação muito lenta: {avg_time*1000:.3f}ms"

    @pytest.mark.parametrize("num_operations", [10, 100, 500])
    def test_scalability_with_increasing_load(self, num_operations):
        """
        Testa escalabilidade com carga crescente.
        Demonstra: Validação de escalabilidade linear.
        """
        cpf = "11144477735"

        start = time.perf_counter()
        for _ in range(num_operations):
            Validator.validate_cpf(cpf)
        end = time.perf_counter()

        total_time = end - start
        avg_time = total_time / num_operations

        # Tempo médio não deve crescer linearmente
        max_avg_time = 0.001  # 1ms por operação
        assert avg_time < max_avg_time, \
            f"Performance degrada com {num_operations} ops: {avg_time*1000:.3f}ms/op"
