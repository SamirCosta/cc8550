import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os
import gc
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from main import app
from src.config import Database

# Importar fixtures necessárias
from tests.fixtures.test_data import (
    valid_cpfs,
    valid_emails,
    valid_license_plates
)


@pytest.fixture(scope="function")
def client():
    """
    Fixture que retorna um client de teste para a API.
    Cada teste recebe uma instância limpa do banco de dados.
    Usa a mesma estratégia da fixture test_db para garantir compatibilidade.
    """
    # Usa um nome único para cada teste (compatível com Windows)
    test_db_path = f"test_functional_api_{uuid.uuid4().hex[:8]}.db"

    # Configurar banco de teste
    db = Database()
    db.db_path = test_db_path
    db._conn = None  # Reset connection
    db.initialize_schema()

    # Criar client
    test_client = TestClient(app)

    yield test_client

    # Cleanup - fecha a conexão antes de remover o arquivo (Windows)
    if hasattr(db, '_conn') and db._conn:
        db._conn.close()
        db._conn = None

    # Força garbage collection para liberar recursos
    gc.collect()

    # Limpeza
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            # No Windows, às vezes o arquivo ainda está em uso
            pass


class TestCarEndpoints:
    """
    Testes funcionais (caixa-preta) para endpoints de carros.
    Usa fixtures do diretório tests/fixtures/ para dados de teste.
    """

    def test_create_car_success(self, client, valid_license_plates):
        """Testa criação de carro via API."""
        response = client.post("/cars/", json={
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "license_plate": valid_license_plates[0],
            "daily_rate": 150.0,
            "is_available": True
        })
        assert response.status_code == 201
        data = response.json()
        assert data["brand"] == "Toyota"
        assert data["id"] is not None

    def test_get_car_success(self, client):
        """Testa busca de carro via API."""
        create_response = client.post("/cars/", json={
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "license_plate": "API2345",
            "daily_rate": 180.0
        })
        car_id = create_response.json()["id"]

        response = client.get(f"/cars/{car_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == car_id
        assert data["brand"] == "Honda"

    def test_get_car_not_found(self, client):
        """Testa busca de carro inexistente."""
        response = client.get("/cars/99999")
        assert response.status_code == 404

    def test_list_all_cars(self, client):
        """Testa listagem de todos os carros."""
        response = client.get("/cars/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_available_cars_with_filters(self, client):
        """Testa busca de carros disponíveis com filtros."""
        response = client.get("/cars/available/search?brand=Toyota&max_price=200")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_car_success(self, client):
        """Testa atualização de carro via API."""
        create_response = client.post("/cars/", json={
            "brand": "Volkswagen",
            "model": "Gol",
            "year": 2023,
            "license_plate": "API3456",
            "daily_rate": 100.0
        })
        car_id = create_response.json()["id"]

        response = client.put(f"/cars/{car_id}", json={
            "daily_rate": 120.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["daily_rate"] == 120.0

    def test_delete_car_success(self, client):
        """Testa remoção de carro via API."""
        create_response = client.post("/cars/", json={
            "brand": "Fiat",
            "model": "Uno",
            "year": 2023,
            "license_plate": "API4567",
            "daily_rate": 90.0
        })
        car_id = create_response.json()["id"]

        response = client.delete(f"/cars/{car_id}")
        assert response.status_code == 204

        get_response = client.get(f"/cars/{car_id}")
        assert get_response.status_code == 404


class TestCustomerEndpoints:
    """
    Testes funcionais (caixa-preta) para endpoints de clientes.
    Usa fixtures do diretório tests/fixtures/ para dados de teste.
    """

    def test_create_customer_success(self, client, valid_cpfs, valid_emails):
        """Testa criação de cliente via API."""
        response = client.post("/customers/", json={
            "name": "João Silva",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "João Silva"
        assert data["id"] is not None

    def test_create_customer_duplicate_cpf(self, client, valid_cpfs, valid_emails):
        """Testa criação de cliente com CPF duplicado."""
        client.post("/customers/", json={
            "name": "Cliente 1",
            "cpf": valid_cpfs[1],
            "phone": "11987654321",
            "email": valid_emails[1]
        })

        response = client.post("/customers/", json={
            "name": "Cliente 2",
            "cpf": valid_cpfs[1],
            "phone": "11999887766",
            "email": valid_emails[2]
        })
        assert response.status_code == 422

    def test_get_customer_success(self, client, valid_cpfs, valid_emails):
        """Testa busca de cliente via API."""
        create_response = client.post("/customers/", json={
            "name": "Maria Santos",
            "cpf": valid_cpfs[2],
            "phone": "11987654321",
            "email": valid_emails[2]
        })
        customer_id = create_response.json()["id"]

        response = client.get(f"/customers/{customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["name"] == "Maria Santos"


class TestRentalEndpoints:
    """
    Testes funcionais (caixa-preta) para endpoints de aluguéis.
    Usa fixtures do diretório tests/fixtures/ para dados de teste.
    """

    def test_create_rental_success(self, client, valid_cpfs, valid_emails):
        """Testa criação de aluguel via API."""
        car_response = client.post("/cars/", json={
            "brand": "Renault",
            "model": "Sandero",
            "year": 2023,
            "license_plate": "RNT5678",
            "daily_rate": 110.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Cliente Rental",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        start_date = (datetime.now() + timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=11)).isoformat()

        response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": start_date,
            "end_date": end_date
        })
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == customer_id
        assert data["car_id"] == car_id
        assert data["status"] == "active"
        assert data["total_value"] > 0

    def test_search_rentals_with_filters(self, client):
        """Testa busca de aluguéis com filtros."""
        response = client.get("/rentals/search/filter?status=active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_complete_rental_success(self, client, valid_cpfs, valid_emails):
        """Testa finalização de aluguel via API."""
        car_response = client.post("/cars/", json={
            "brand": "Peugeot",
            "model": "208",
            "year": 2023,
            "license_plate": "CMP6789",
            "daily_rate": 130.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Complete Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        start_date = (datetime.now() + timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=6)).isoformat()

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": start_date,
            "end_date": end_date
        })
        rental_id = rental_response.json()["id"]

        response = client.post(f"/rentals/{rental_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestPaymentEndpoints:
    """
    Testes funcionais (caixa-preta) para endpoints de pagamentos.
    Usa fixtures do diretório tests/fixtures/ para dados de teste.
    """

    def test_create_payment_success(self, client, valid_cpfs, valid_emails):
        """Testa criação de pagamento via API."""
        car_response = client.post("/cars/", json={
            "brand": "Citroën",
            "model": "C3",
            "year": 2023,
            "license_plate": "PAY7890",
            "daily_rate": 120.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Payment Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        start_date = (datetime.now() + timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=6)).isoformat()

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": start_date,
            "end_date": end_date
        })
        rental_id = rental_response.json()["id"]
        total_value = rental_response.json()["total_value"]

        response = client.post("/payments/", json={
            "rental_id": rental_id,
            "amount": total_value,
            "payment_method": "credit_card",
            "payment_date": datetime.now().isoformat(),
            "status": "pending"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["rental_id"] == rental_id
        assert data["status"] == "pending"

    def test_process_payment_success(self, client, valid_cpfs, valid_emails):
        """Testa processamento de pagamento via API."""
        car_response = client.post("/cars/", json={
            "brand": "Hyundai",
            "model": "HB20",
            "year": 2023,
            "license_plate": "PRC8901",
            "daily_rate": 105.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Process Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        start_date = (datetime.now() + timedelta(days=1)).isoformat()
        end_date = (datetime.now() + timedelta(days=6)).isoformat()

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": start_date,
            "end_date": end_date
        })
        rental_id = rental_response.json()["id"]
        total_value = rental_response.json()["total_value"]

        payment_response = client.post("/payments/", json={
            "rental_id": rental_id,
            "amount": total_value,
            "payment_method": "pix",
            "payment_date": datetime.now().isoformat()
        })
        payment_id = payment_response.json()["id"]

        response = client.post(f"/payments/{payment_id}/process")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestMaintenanceEndpoints:
    """
    Testes funcionais (caixa-preta) para endpoints de manutenções.
    """

    def test_create_maintenance_success(self, client):
        """Testa criação de manutenção via API."""
        car_response = client.post("/cars/", json={
            "brand": "Jeep",
            "model": "Renegade",
            "year": 2023,
            "license_plate": "MNT9012",
            "daily_rate": 200.0
        })
        car_id = car_response.json()["id"]

        response = client.post("/maintenances/", json={
            "car_id": car_id,
            "description": "Revisão dos 10.000km",
            "maintenance_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "cost": 450.0,
            "status": "scheduled"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["car_id"] == car_id
        assert data["description"] == "Revisão dos 10.000km"

    def test_complete_maintenance_success(self, client):
        """Testa finalização de manutenção via API."""
        car_response = client.post("/cars/", json={
            "brand": "Mitsubishi",
            "model": "Lancer",
            "year": 2023,
            "license_plate": "CPM0123",
            "daily_rate": 170.0
        })
        car_id = car_response.json()["id"]

        maintenance_response = client.post("/maintenances/", json={
            "car_id": car_id,
            "description": "Balanceamento",
            "maintenance_date": datetime.now().isoformat(),
            "cost": 200.0,
            "status": "in_progress"
        })
        maintenance_id = maintenance_response.json()["id"]

        response = client.post(f"/maintenances/{maintenance_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_get_maintenance_success(self, client):
        """Testa busca de manutenção por ID via API."""
        car_response = client.post("/cars/", json={
            "brand": "BMW",
            "model": "320i",
            "year": 2023,
            "license_plate": "GET1234",
            "daily_rate": 300.0
        })
        car_id = car_response.json()["id"]

        create_response = client.post("/maintenances/", json={
            "car_id": car_id,
            "description": "Troca de óleo",
            "maintenance_date": datetime.now().isoformat(),
            "cost": 250.0,
            "status": "scheduled"
        })
        maintenance_id = create_response.json()["id"]

        response = client.get(f"/maintenances/{maintenance_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == maintenance_id
        assert data["description"] == "Troca de óleo"

    def test_list_all_maintenances(self, client):
        """Testa listagem de todas as manutenções."""
        response = client.get("/maintenances/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_maintenances_by_car(self, client):
        """Testa busca de manutenções por carro."""
        car_response = client.post("/cars/", json={
            "brand": "Audi",
            "model": "A3",
            "year": 2023,
            "license_plate": "CAR5678",
            "daily_rate": 280.0
        })
        car_id = car_response.json()["id"]

        client.post("/maintenances/", json={
            "car_id": car_id,
            "description": "Alinhamento",
            "maintenance_date": datetime.now().isoformat(),
            "cost": 150.0,
            "status": "scheduled"
        })

        response = client.get(f"/maintenances/car/{car_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestAdditionalEndpoints:
    """
    Testes adicionais para endpoints não cobertos anteriormente.
    Usa fixtures do diretório tests/fixtures/ para dados de teste.
    """

    def test_list_all_customers(self, client):
        """Testa listagem de todos os clientes."""
        response = client.get("/customers/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_update_customer_success(self, client, valid_cpfs, valid_emails):
        """Testa atualização de cliente via API."""
        create_response = client.post("/customers/", json={
            "name": "Update Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = create_response.json()["id"]

        response = client.put(f"/customers/{customer_id}", json={
            "phone": "11999999999"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "11999999999"

    def test_delete_customer_success(self, client, valid_cpfs, valid_emails):
        """Testa remoção de cliente via API."""
        create_response = client.post("/customers/", json={
            "name": "Delete Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = create_response.json()["id"]

        response = client.delete(f"/customers/{customer_id}")
        assert response.status_code == 204

        get_response = client.get(f"/customers/{customer_id}")
        assert get_response.status_code == 404

    def test_list_all_rentals(self, client):
        """Testa listagem de todos os aluguéis."""
        response = client.get("/rentals/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_rental_success(self, client, valid_cpfs, valid_emails):
        """Testa busca de aluguel por ID via API."""
        car_response = client.post("/cars/", json={
            "brand": "Kia",
            "model": "Sportage",
            "year": 2023,
            "license_plate": "RNT1122",
            "daily_rate": 180.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Get Rental Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        create_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat()
        })
        rental_id = create_response.json()["id"]

        response = client.get(f"/rentals/{rental_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rental_id

    def test_cancel_rental_success(self, client, valid_cpfs, valid_emails):
        """Testa cancelamento de aluguel via API."""
        car_response = client.post("/cars/", json={
            "brand": "Mazda",
            "model": "CX-5",
            "year": 2023,
            "license_plate": "CNL3344",
            "daily_rate": 190.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Cancel Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat()
        })
        rental_id = rental_response.json()["id"]

        response = client.post(f"/rentals/{rental_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_list_all_payments(self, client):
        """Testa listagem de todos os pagamentos."""
        response = client.get("/payments/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_payment_success(self, client, valid_cpfs, valid_emails):
        """Testa busca de pagamento por ID via API."""
        car_response = client.post("/cars/", json={
            "brand": "Subaru",
            "model": "Impreza",
            "year": 2023,
            "license_plate": "PAY5566",
            "daily_rate": 160.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Payment Get Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat()
        })
        rental_id = rental_response.json()["id"]
        total_value = rental_response.json()["total_value"]

        create_response = client.post("/payments/", json={
            "rental_id": rental_id,
            "amount": total_value,
            "payment_method": "debit_card",
            "payment_date": datetime.now().isoformat()
        })
        payment_id = create_response.json()["id"]

        response = client.get(f"/payments/{payment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id

    def test_get_payments_by_rental(self, client, valid_cpfs, valid_emails):
        """Testa busca de pagamentos por aluguel."""
        car_response = client.post("/cars/", json={
            "brand": "Volvo",
            "model": "XC40",
            "year": 2023,
            "license_plate": "RNT7788",
            "daily_rate": 250.0
        })
        car_id = car_response.json()["id"]

        customer_response = client.post("/customers/", json={
            "name": "Rental Payment Test",
            "cpf": valid_cpfs[0],
            "phone": "11987654321",
            "email": valid_emails[0]
        })
        customer_id = customer_response.json()["id"]

        rental_response = client.post("/rentals/", json={
            "customer_id": customer_id,
            "car_id": car_id,
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6)).isoformat()
        })
        rental_id = rental_response.json()["id"]
        total_value = rental_response.json()["total_value"]

        client.post("/payments/", json={
            "rental_id": rental_id,
            "amount": total_value,
            "payment_method": "cash",
            "payment_date": datetime.now().isoformat()
        })

        response = client.get(f"/payments/rental/{rental_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
