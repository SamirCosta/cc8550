"""
Testes de mutação para RentalController.

Este módulo contém testes essenciais para detectar mutações críticas no código
do RentalController.

Categorias de mutação testadas:
1. Códigos de status HTTP (201, 204, 404)
2. Tratamento de exceções
3. Validações de entrada
4. Mapeamento de dados
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from src.controllers.rental_controller import router
from src.models import Rental
from src.utils import NotFoundException, ValidationException


# Cria app de teste
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRentalControllerCriticalMutations:
    """Testes essenciais para detectar mutações críticas."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_create_status_code_mutation(self, mock_service):
        """Detecta mutação: status_code=201 -> status_code=200"""
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1, 'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05',
            'total_value': 500.0, 'status': 'active'
        }
        mock_service.create_rental.return_value = mock_rental

        response = client.post('/rentals/', json={
            'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05'
        })

        assert response.status_code == 201, "Mutação detectada: status code deveria ser 201"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_delete_status_code_mutation(self, mock_service):
        """Detecta mutação: status_code=204 -> status_code=200"""
        mock_service.delete_rental.return_value = True
        response = client.delete('/rentals/1')
        assert response.status_code == 204, "Mutação detectada: status code deveria ser 204"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_not_found_exception_handling_mutation(self, mock_service):
        """Detecta mutação: NotFoundException -> outro tipo de exceção"""
        mock_service.get_rental.side_effect = NotFoundException("Aluguel com ID 999 não encontrado")
        response = client.get('/rentals/999')
        assert response.status_code == 404, "Mutação detectada: exceção não tratada corretamente"
        assert "não encontrado" in response.json()['detail']

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_validation_exception_handling_mutation(self, mock_service):
        """Detecta mutação: ValidationException -> outro tipo de exceção"""
        mock_service.create_rental.side_effect = ValidationException("Dados inválidos")
        response = client.post('/rentals/', json={
            'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05'
        })
        assert response.status_code == 400, "Mutação detectada: exceção não tratada corretamente"

    def test_detect_required_field_mutation_customer_id(self):
        """Detecta mutação: Field(..., gt=0) -> Field(None, gt=0)"""
        response = client.post('/rentals/', json={
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })
        assert response.status_code == 422, "Mutação detectada: campo obrigatório removido"

    def test_detect_gt_validation_mutation_customer_id(self):
        """Detecta mutação: gt=0 -> gt=1 ou remoção de gt"""
        response = client.post('/rentals/', json={
            'customer_id': 0, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05'
        })
        assert response.status_code == 422, "Mutação detectada: validação gt alterada"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_to_dict_mutation_in_response(self, mock_service):
        """Detecta mutação: rental.to_dict() -> rental"""
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1, 'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05',
            'total_value': 500.0, 'status': 'active'
        }
        mock_service.get_rental.return_value = mock_rental

        response = client.get('/rentals/1')
        mock_rental.to_dict.assert_called_once()
        assert response.status_code == 200
