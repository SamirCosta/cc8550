import pytest
from datetime import datetime, timedelta
from src.services import CarService, CustomerService, RentalService, PaymentService, MaintenanceService
from src.utils import BusinessRuleException

# Importar fixtures necessárias
from tests.fixtures.database import test_db
from tests.fixtures.test_data import valid_cpfs, valid_emails


class TestRentalCompleteFlow:
    """
    Testes de integração para o fluxo completo de aluguel.
    Usa fixtures do diretório tests/fixtures/ para garantir consistência.
    """

    def test_complete_rental_workflow(self, test_db, valid_cpfs, valid_emails):
        """
        Testa o fluxo completo: criar carro, cliente, aluguel, pagamento e finalizar.
        """
        car_service = CarService()
        customer_service = CustomerService()
        rental_service = RentalService()
        payment_service = PaymentService()

        car_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "license_plate": "ABC1234",
            "daily_rate": 150.0
        }
        car = car_service.create_car(car_data)
        assert car.id is not None

        customer_data = {
            "name": "João Silva",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        }
        customer = customer_service.create_customer(customer_data)
        assert customer.id is not None

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=10)

        rental_data = {
            "customer_id": customer.id,
            "car_id": car.id,
            "start_date": start_date,
            "end_date": end_date
        }
        rental = rental_service.create_rental(rental_data)
        assert rental.id is not None
        assert rental.total_value > 0

        updated_car = car_service.get_car(car.id)
        assert updated_car.is_available is False

        payment_data = {
            "rental_id": rental.id,
            "amount": rental.total_value,
            "payment_method": "credit_card",
            "payment_date": datetime.now()
        }
        payment = payment_service.create_payment(payment_data)
        assert payment.id is not None

        processed_payment = payment_service.process_payment(payment.id)
        assert processed_payment.status == "completed"

        completed_rental = rental_service.complete_rental(rental.id)
        assert completed_rental.status == "completed"

        final_car = car_service.get_car(car.id)
        assert final_car.is_available is True

    def test_rental_prevents_duplicate_booking(self, test_db, valid_cpfs, valid_emails):
        """
        Testa que não é possível alugar um carro já alugado.
        """
        car_service = CarService()
        customer_service = CustomerService()
        rental_service = RentalService()

        car_data = {
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "license_plate": "XYZ5678",
            "daily_rate": 180.0
        }
        car = car_service.create_car(car_data)

        customer1_data = {
            "name": "Cliente 1",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        }
        customer1 = customer_service.create_customer(customer1_data)

        customer2_data = {
            "name": "Cliente 2",
            "cpf": valid_cpfs[1],
            "phone": "11999887766",
            "email": valid_emails[1]
        }
        customer2 = customer_service.create_customer(customer2_data)

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=5)

        rental1_data = {
            "customer_id": customer1.id,
            "car_id": car.id,
            "start_date": start_date,
            "end_date": end_date
        }
        rental_service.create_rental(rental1_data)

        rental2_data = {
            "customer_id": customer2.id,
            "car_id": car.id,
            "start_date": start_date,
            "end_date": end_date
        }

        with pytest.raises(BusinessRuleException, match="não está disponível"):
            rental_service.create_rental(rental2_data)

    def test_customer_with_pending_payment_cannot_rent(self, test_db, valid_cpfs, valid_emails):
        """
        Testa que cliente com pagamento pendente não pode alugar.
        """
        car_service = CarService()
        customer_service = CustomerService()
        rental_service = RentalService()
        payment_service = PaymentService()

        car1_data = {
            "brand": "Ford",
            "model": "Focus",
            "year": 2023,
            "license_plate": "DEF1111",
            "daily_rate": 120.0
        }
        car1 = car_service.create_car(car1_data)

        car2_data = {
            "brand": "Chevrolet",
            "model": "Onix",
            "year": 2023,
            "license_plate": "GHI2222",
            "daily_rate": 100.0
        }
        car2 = car_service.create_car(car2_data)

        customer_data = {
            "name": "Maria Santos",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        }
        customer = customer_service.create_customer(customer_data)

        start_date1 = datetime.now() + timedelta(days=1)
        end_date1 = start_date1 + timedelta(days=5)

        rental1_data = {
            "customer_id": customer.id,
            "car_id": car1.id,
            "start_date": start_date1,
            "end_date": end_date1
        }
        rental1 = rental_service.create_rental(rental1_data)

        payment_data = {
            "rental_id": rental1.id,
            "amount": rental1.total_value,
            "payment_method": "pix",
            "payment_date": datetime.now(),
            "status": "pending"
        }
        payment_service.create_payment(payment_data)

        start_date2 = datetime.now() + timedelta(days=10)
        end_date2 = start_date2 + timedelta(days=5)

        rental2_data = {
            "customer_id": customer.id,
            "car_id": car2.id,
            "start_date": start_date2,
            "end_date": end_date2
        }

        with pytest.raises(BusinessRuleException, match="pagamento pendente"):
            rental_service.create_rental(rental2_data)


class TestMaintenanceIntegration:
    """
    Testes de integração para manutenção de carros.
    Usa fixtures do diretório tests/fixtures/ para garantir consistência.
    """

    def test_car_with_maintenance_cannot_be_rented(self, test_db, valid_cpfs, valid_emails):
        """
        Testa que carro com manutenção agendada não pode ser alugado.
        """
        car_service = CarService()
        customer_service = CustomerService()
        rental_service = RentalService()
        maintenance_service = MaintenanceService()

        car_data = {
            "brand": "Volkswagen",
            "model": "Gol",
            "year": 2023,
            "license_plate": "JKL3333",
            "daily_rate": 90.0
        }
        car = car_service.create_car(car_data)

        maintenance_data = {
            "car_id": car.id,
            "description": "Revisão completa",
            "maintenance_date": datetime.now() + timedelta(days=3),
            "cost": 500.0,
            "status": "scheduled"
        }
        maintenance_service.create_maintenance(maintenance_data)

        customer_data = {
            "name": "Pedro Oliveira",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        }
        customer = customer_service.create_customer(customer_data)

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=5)

        rental_data = {
            "customer_id": customer.id,
            "car_id": car.id,
            "start_date": start_date,
            "end_date": end_date
        }

        with pytest.raises(BusinessRuleException, match="não está disponível"):
            rental_service.create_rental(rental_data)

    def test_complete_maintenance_makes_car_available(self, test_db):
        """
        Testa que finalizar manutenção torna o carro disponível.
        """
        car_service = CarService()
        maintenance_service = MaintenanceService()

        car_data = {
            "brand": "Fiat",
            "model": "Uno",
            "year": 2023,
            "license_plate": "MNO4444",
            "daily_rate": 80.0
        }
        car = car_service.create_car(car_data)

        maintenance_data = {
            "car_id": car.id,
            "description": "Troca de pneus",
            "maintenance_date": datetime.now(),
            "cost": 800.0,
            "status": "in_progress"
        }
        maintenance = maintenance_service.create_maintenance(maintenance_data)

        updated_car = car_service.get_car(car.id)
        assert updated_car.is_available is False

        maintenance_service.complete_maintenance(maintenance.id)

        final_car = car_service.get_car(car.id)
        assert final_car.is_available is True


class TestDiscountCalculation:
    """
    Testes de integração para cálculo de descontos.
    Usa fixtures do diretório tests/fixtures/ para garantir consistência.
    """

    @pytest.mark.parametrize("days,expected_discount_rate", [
        (3, 0.0),
        (10, 0.10),
        (20, 0.15),
        (40, 0.20)
    ])
    def test_rental_discount_calculation(self, test_db, days, expected_discount_rate, valid_cpfs, valid_emails):
        """
        Testa cálculo de desconto para diferentes períodos.
        """
        car_service = CarService()
        customer_service = CustomerService()
        rental_service = RentalService()

        car_data = {
            "brand": "Nissan",
            "model": "Versa",
            "year": 2023,
            "license_plate": f"PQR{days:04d}",
            "daily_rate": 100.0
        }
        car = car_service.create_car(car_data)

        customer_data = {
            "name": f"Cliente {days}",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        }
        customer = customer_service.create_customer(customer_data)

        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=days)

        rental_data = {
            "customer_id": customer.id,
            "car_id": car.id,
            "start_date": start_date,
            "end_date": end_date
        }
        rental = rental_service.create_rental(rental_data)

        expected_value = 100.0 * days * (1 - expected_discount_rate)
        assert rental.total_value == pytest.approx(expected_value, rel=0.01)
