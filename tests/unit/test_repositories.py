import pytest
from src.utils import NotFoundException

# Importar fixtures necessárias
from tests.fixtures.database import test_db
from tests.fixtures.repositories import (
    car_repository,
    customer_repository,
    rental_repository,
    payment_repository,
    maintenance_repository
)
from tests.fixtures.models import (
    sample_car,
    sample_customer,
    sample_maintenance,
    sample_payment,
    create_test_car,
    create_test_customer,
    create_test_rental
)


class TestCarRepository:
    """
    Testes unitários para CarRepository.
    """

    def test_create_car(self, car_repository, sample_car):
        """Testa criação de um carro."""
        created_car = car_repository.create(sample_car)
        assert created_car.id is not None
        assert created_car.brand == "Toyota"

    def test_find_car_by_id(self, car_repository, create_test_car):
        """Testa busca de carro por ID."""
        found_car = car_repository.find_by_id(create_test_car.id)
        assert found_car.id == create_test_car.id
        assert found_car.license_plate == create_test_car.license_plate

    def test_find_car_by_id_not_found(self, car_repository):
        """Testa busca de carro inexistente."""
        with pytest.raises(NotFoundException, match="Carro com ID 999 não encontrado"):
            car_repository.find_by_id(999)

    def test_find_all_cars(self, car_repository, sample_car):
        """Testa listagem de todos os carros."""
        car_repository.create(sample_car)
        cars = car_repository.find_all()
        assert len(cars) >= 1

    def test_update_car(self, car_repository, create_test_car):
        """Testa atualização de um carro."""
        create_test_car.daily_rate = 200.0
        updated_car = car_repository.update(create_test_car)
        assert updated_car.daily_rate == 200.0

    def test_delete_car(self, car_repository, create_test_car):
        """Testa remoção de um carro."""
        car_id = create_test_car.id
        result = car_repository.delete(car_id)
        assert result is True
        with pytest.raises(NotFoundException):
            car_repository.find_by_id(car_id)

    def test_find_by_license_plate(self, car_repository, create_test_car):
        """Testa busca por placa."""
        found_car = car_repository.find_by_license_plate(create_test_car.license_plate)
        assert found_car is not None
        assert found_car.id == create_test_car.id

    def test_find_by_license_plate_not_found(self, car_repository):
        """Testa busca por placa inexistente."""
        result = car_repository.find_by_license_plate("ZZZ9999")
        assert result is None

    def test_update_availability(self, car_repository, create_test_car):
        """Testa atualização de disponibilidade."""
        result = car_repository.update_availability(create_test_car.id, False)
        assert result is True
        car = car_repository.find_by_id(create_test_car.id)
        assert car.is_available is False


class TestCustomerRepository:
    """
    Testes unitários para CustomerRepository.
    """

    def test_create_customer(self, customer_repository, sample_customer):
        """Testa criação de um cliente."""
        created_customer = customer_repository.create(sample_customer)
        assert created_customer.id is not None
        assert created_customer.name == "João Silva"

    def test_find_customer_by_id(self, customer_repository, create_test_customer):
        """Testa busca de cliente por ID."""
        found_customer = customer_repository.find_by_id(create_test_customer.id)
        assert found_customer.id == create_test_customer.id
        assert found_customer.cpf == create_test_customer.cpf

    def test_find_customer_by_id_not_found(self, customer_repository):
        """Testa busca de cliente inexistente."""
        with pytest.raises(NotFoundException):
            customer_repository.find_by_id(999)

    def test_find_all_customers(self, customer_repository, sample_customer):
        """Testa listagem de todos os clientes."""
        customer_repository.create(sample_customer)
        customers = customer_repository.find_all()
        assert len(customers) >= 1

    def test_update_customer(self, customer_repository, create_test_customer):
        """Testa atualização de um cliente."""
        create_test_customer.phone = "11999999999"
        updated_customer = customer_repository.update(create_test_customer)
        assert updated_customer.phone == "11999999999"

    def test_delete_customer(self, customer_repository, create_test_customer):
        """Testa remoção de um cliente."""
        customer_id = create_test_customer.id
        result = customer_repository.delete(customer_id)
        assert result is True
        with pytest.raises(NotFoundException):
            customer_repository.find_by_id(customer_id)

    def test_find_by_cpf(self, customer_repository, create_test_customer):
        """Testa busca por CPF."""
        found_customer = customer_repository.find_by_cpf(create_test_customer.cpf)
        assert found_customer is not None
        assert found_customer.id == create_test_customer.id

    def test_find_by_email(self, customer_repository, create_test_customer):
        """Testa busca por email."""
        found_customer = customer_repository.find_by_email(create_test_customer.email)
        assert found_customer is not None
        assert found_customer.id == create_test_customer.id

    def test_update_payment_status(self, customer_repository, create_test_customer):
        """Testa atualização de status de pagamento."""
        result = customer_repository.update_payment_status(create_test_customer.id, True)
        assert result is True
        customer = customer_repository.find_by_id(create_test_customer.id)
        assert customer.has_pending_payment is True


class TestRentalRepository:
    """
    Testes unitários para RentalRepository.
    """

    def test_create_rental(self, rental_repository, create_test_rental):
        """Testa criação de um aluguel."""
        assert create_test_rental.id is not None
        assert create_test_rental.status == "active"

    def test_find_rental_by_id(self, rental_repository, create_test_rental):
        """Testa busca de aluguel por ID."""
        found_rental = rental_repository.find_by_id(create_test_rental.id)
        assert found_rental.id == create_test_rental.id
        assert found_rental.customer_id == create_test_rental.customer_id

    def test_find_all_rentals(self, rental_repository, create_test_rental):
        """Testa listagem de todos os aluguéis."""
        rentals = rental_repository.find_all()
        assert len(rentals) >= 1

    def test_update_rental_status(self, rental_repository, create_test_rental):
        """Testa atualização de status de aluguel."""
        result = rental_repository.update_status(create_test_rental.id, "completed")
        assert result is True
        rental = rental_repository.find_by_id(create_test_rental.id)
        assert rental.status == "completed"

    def test_find_by_customer(self, rental_repository, create_test_rental):
        """Testa busca de aluguéis por cliente."""
        rentals = rental_repository.find_by_customer(create_test_rental.customer_id)
        assert len(rentals) >= 1
        assert rentals[0].customer_id == create_test_rental.customer_id

    def test_find_by_car(self, rental_repository, create_test_rental):
        """Testa busca de aluguéis por carro."""
        rentals = rental_repository.find_by_car(create_test_rental.car_id)
        assert len(rentals) >= 1
        assert rentals[0].car_id == create_test_rental.car_id


class TestPaymentRepository:
    """
    Testes unitários para PaymentRepository.
    """

    def test_create_payment(self, payment_repository, create_test_rental, sample_payment):
        """Testa criação de um pagamento."""
        sample_payment.rental_id = create_test_rental.id
        created_payment = payment_repository.create(sample_payment)
        assert created_payment.id is not None
        assert created_payment.amount == 1500.0

    def test_find_payment_by_id(self, payment_repository, create_test_rental, sample_payment):
        """Testa busca de pagamento por ID."""
        sample_payment.rental_id = create_test_rental.id
        created_payment = payment_repository.create(sample_payment)
        found_payment = payment_repository.find_by_id(created_payment.id)
        assert found_payment.id == created_payment.id

    def test_update_payment_status(self, payment_repository, create_test_rental, sample_payment):
        """Testa atualização de status de pagamento."""
        sample_payment.rental_id = create_test_rental.id
        created_payment = payment_repository.create(sample_payment)
        result = payment_repository.update_status(created_payment.id, "completed")
        assert result is True
        payment = payment_repository.find_by_id(created_payment.id)
        assert payment.status == "completed"


class TestMaintenanceRepository:
    """
    Testes unitários para MaintenanceRepository.
    """

    def test_create_maintenance(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa criação de uma manutenção."""
        sample_maintenance.car_id = create_test_car.id
        created_maintenance = maintenance_repository.create(sample_maintenance)
        assert created_maintenance.id is not None
        assert created_maintenance.cost == 300.0

    def test_find_maintenance_by_id(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa busca de manutenção por ID."""
        sample_maintenance.car_id = create_test_car.id
        created_maintenance = maintenance_repository.create(sample_maintenance)
        found_maintenance = maintenance_repository.find_by_id(created_maintenance.id)
        assert found_maintenance.id == created_maintenance.id

    def test_find_by_car(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa busca de manutenções por carro."""
        sample_maintenance.car_id = create_test_car.id
        maintenance_repository.create(sample_maintenance)
        maintenances = maintenance_repository.find_by_car(create_test_car.id)
        assert len(maintenances) >= 1

    def test_update_maintenance_status(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa atualização de status de manutenção."""
        sample_maintenance.car_id = create_test_car.id
        created_maintenance = maintenance_repository.create(sample_maintenance)
        result = maintenance_repository.update_status(created_maintenance.id, "completed")
        assert result is True
        maintenance = maintenance_repository.find_by_id(created_maintenance.id)
        assert maintenance.status == "completed"

    def test_update_maintenance(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa atualização completa de manutenção."""
        sample_maintenance.car_id = create_test_car.id
        created = maintenance_repository.create(sample_maintenance)
        created.cost = 600.0
        created.description = "Revisão atualizada"
        updated = maintenance_repository.update(created)
        assert updated.cost == 600.0
        assert updated.description == "Revisão atualizada"

    def test_delete_maintenance(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa remoção de manutenção."""
        sample_maintenance.car_id = create_test_car.id
        created = maintenance_repository.create(sample_maintenance)
        result = maintenance_repository.delete(created.id)
        assert result is True

    def test_find_active_by_car(self, maintenance_repository, create_test_car, sample_maintenance):
        """Testa busca de manutenções ativas por carro."""
        sample_maintenance.car_id = create_test_car.id
        sample_maintenance.status = "in_progress"
        maintenance_repository.create(sample_maintenance)
        active = maintenance_repository.find_active_by_car(create_test_car.id)
        assert len(active) >= 1


class TestRentalRepositoryExtra:
    """
    Testes adicionais para RentalRepository.
    """

    def test_update_rental(self, rental_repository, create_test_rental):
        """Testa atualização completa de aluguel."""
        create_test_rental.total_value = 1500.0
        create_test_rental.status = "completed"
        updated = rental_repository.update(create_test_rental)
        assert updated.total_value == 1500.0
        assert updated.status == "completed"

    def test_delete_rental(self, rental_repository, create_test_rental):
        """Testa remoção de aluguel."""
        result = rental_repository.delete(create_test_rental.id)
        assert result is True


