"""
Testes de mutação para RentalController.

Este módulo contém testes específicos para detectar mutações no código
do RentalController, verificando se os testes conseguem identificar mudanças
em códigos de status HTTP, tratamento de exceções e validações.

Categorias de mutação testadas:
1. Códigos de status HTTP (200, 201, 204, 400, 404, etc.)
2. Tratamento de exceções (tipos de exceção, mensagens)
3. Validações de entrada (campos obrigatórios, tipos)
4. Mapeamento de dados (conversões, transformações)
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch
from datetime import datetime
from src.controllers.rental_controller import router
from src.models import Rental
from src.utils import (
    NotFoundException,
    ValidationException,
    BusinessRuleException,
    RentalException
)


# Cria app de teste
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestRentalControllerStatusCodeMutations:
    """Testes para detectar mutações em códigos de status HTTP."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_create_status_code_mutation(self, mock_service):
        """
        Detecta mutação: status_code=201 -> status_code=200

        POST para criar recurso deve retornar 201 (Created), não 200 (OK).
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }
        mock_service.create_rental.return_value = mock_rental

        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        assert response.status_code == 201, "Mutação detectada: status code deveria ser 201"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_delete_status_code_mutation(self, mock_service):
        """
        Detecta mutação: status_code=204 -> status_code=200

        DELETE bem-sucedido deve retornar 204 (No Content), não 200 (OK).
        """
        mock_service.delete_rental.return_value = True

        response = client.delete('/rentals/1')

        assert response.status_code == 204, "Mutação detectada: status code deveria ser 204"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_get_status_code_mutation(self, mock_service):
        """
        Detecta mutação: status_code implícito 200 -> outro código

        GET bem-sucedido deve retornar 200 (OK).
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }
        mock_service.get_rental.return_value = mock_rental

        response = client.get('/rentals/1')

        assert response.status_code == 200, "Mutação detectada: status code deveria ser 200"


class TestRentalControllerExceptionMutations:
    """Testes para detectar mutações no tratamento de exceções."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_not_found_exception_handling_mutation(self, mock_service):
        """
        Detecta mutação: NotFoundException -> outro tipo de exceção

        Garante que NotFoundException seja tratada corretamente.
        """
        mock_service.get_rental.side_effect = NotFoundException(
            "Aluguel com ID 999 não encontrado"
        )

        response = client.get('/rentals/999')

        # NotFoundException deve retornar 404
        assert response.status_code == 404, "Mutação detectada: exceção não tratada corretamente"
        assert "não encontrado" in response.json()['detail']

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_validation_exception_handling_mutation(self, mock_service):
        """
        Detecta mutação: ValidationException -> outro tipo de exceção

        Garante que ValidationException seja tratada corretamente.
        """
        mock_service.create_rental.side_effect = ValidationException(
            "Dados inválidos"
        )

        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # ValidationException deve retornar 400
        assert response.status_code == 400, "Mutação detectada: exceção não tratada corretamente"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_business_rule_exception_handling_mutation(self, mock_service):
        """
        Detecta mutação: BusinessRuleException -> outro tipo de exceção

        Garante que BusinessRuleException seja tratada corretamente.
        """
        mock_service.create_rental.side_effect = BusinessRuleException(
            "Cliente possui pagamento pendente"
        )

        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # BusinessRuleException deve retornar 422
        assert response.status_code == 422, "Mutação detectada: exceção não tratada corretamente"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_exception_order_mutation_in_create(self, mock_service):
        """
        Detecta mutação na ordem de tratamento de exceções.

        Garante que exceções mais específicas sejam tratadas antes das genéricas.
        """
        mock_service.create_rental.side_effect = ValidationException(
            "Dados inválidos"
        )

        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Se a ordem estiver errada, pode cair no catch genérico
        assert response.status_code == 400, "Mutação detectada: ordem de exceções incorreta"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_exception_order_mutation_in_complete(self, mock_service):
        """
        Detecta mutação na ordem de tratamento de exceções em complete_rental.

        NotFoundException e BusinessRuleException devem ser tratadas especificamente.
        """
        mock_service.complete_rental.side_effect = BusinessRuleException(
            "Apenas aluguéis ativos podem ser finalizados"
        )

        response = client.post('/rentals/1/complete')

        assert response.status_code == 422, "Mutação detectada: exceção não tratada corretamente"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_exception_order_mutation_in_cancel(self, mock_service):
        """
        Detecta mutação na ordem de tratamento de exceções em cancel_rental.

        NotFoundException e BusinessRuleException devem ser tratadas especificamente.
        """
        mock_service.cancel_rental.side_effect = NotFoundException(
            "Aluguel não encontrado"
        )

        response = client.post('/rentals/999/cancel')

        assert response.status_code == 404, "Mutação detectada: exceção não tratada corretamente"


class TestRentalControllerValidationMutations:
    """Testes para detectar mutações em validações de entrada."""

    def test_detect_required_field_mutation_customer_id(self):
        """
        Detecta mutação: Field(..., gt=0) -> Field(None, gt=0)

        customer_id deve ser obrigatório.
        """
        response = client.post('/rentals/', json={
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Deve retornar erro de validação
        assert response.status_code == 422, "Mutação detectada: campo obrigatório removido"

    def test_detect_required_field_mutation_car_id(self):
        """
        Detecta mutação: Field(..., gt=0) -> Field(None, gt=0)

        car_id deve ser obrigatório.
        """
        response = client.post('/rentals/', json={
            'customer_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Deve retornar erro de validação
        assert response.status_code == 422, "Mutação detectada: campo obrigatório removido"

    def test_detect_gt_validation_mutation_customer_id(self):
        """
        Detecta mutação: gt=0 -> gt=1 ou remoção de gt

        customer_id deve ser maior que 0.
        """
        response = client.post('/rentals/', json={
            'customer_id': 0,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Deve retornar erro de validação
        assert response.status_code == 422, "Mutação detectada: validação gt alterada"

    def test_detect_gt_validation_mutation_car_id(self):
        """
        Detecta mutação: gt=0 -> gt=1 ou remoção de gt

        car_id deve ser maior que 0.
        """
        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': -1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Deve retornar erro de validação
        assert response.status_code == 422, "Mutação detectada: validação gt alterada"


class TestRentalControllerDataMappingMutations:
    """Testes para detectar mutações no mapeamento de dados."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_dict_conversion_mutation_in_create(self, mock_service):
        """
        Detecta mutação: rental_data.dict() -> rental_data

        Deve converter Pydantic model para dict antes de passar ao service.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }
        mock_service.create_rental.return_value = mock_rental

        response = client.post('/rentals/', json={
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05'
        })

        # Verifica se .dict() foi chamado
        call_args = mock_service.create_rental.call_args[0][0]
        assert isinstance(call_args, dict), "Mutação detectada: conversão para dict não realizada"

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_to_dict_mutation_in_response(self, mock_service):
        """
        Detecta mutação: rental.to_dict() -> rental

        Deve converter modelo para dict na resposta.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }
        mock_service.get_rental.return_value = mock_rental

        response = client.get('/rentals/1')

        # Verifica se to_dict foi chamado
        mock_rental.to_dict.assert_called_once()
        assert response.status_code == 200

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_list_comprehension_mutation_in_get_all(self, mock_service):
        """
        Detecta mutação: [rental.to_dict() for rental in rentals] -> rentals

        Deve converter lista de modelos para lista de dicts.
        """
        mock_rental1 = Mock(spec=Rental)
        mock_rental1.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }

        mock_rental2 = Mock(spec=Rental)
        mock_rental2.to_dict.return_value = {
            'id': 2,
            'customer_id': 2,
            'car_id': 2,
            'start_date': '2025-01-10',
            'end_date': '2025-01-15',
            'total_value': 600.0,
            'status': 'active'
        }

        mock_service.get_all_rentals.return_value = [mock_rental1, mock_rental2]

        response = client.get('/rentals/')

        # Verifica se to_dict foi chamado para cada item
        assert len(response.json()) == 2
        mock_rental1.to_dict.assert_called_once()
        mock_rental2.to_dict.assert_called_once()


class TestRentalControllerFilterMutations:
    """Testes para detectar mutações na lógica de filtros."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_filter_condition_mutation(self, mock_service):
        """
        Detecta mutação: if customer_id: -> if not customer_id:

        Filtros devem ser adicionados quando os parâmetros estão presentes.
        """
        mock_service.search_rentals.return_value = []

        response = client.get('/rentals/search/filter?customer_id=1')

        # Verifica se o filtro foi passado corretamente
        call_args = mock_service.search_rentals.call_args[0][0]
        assert 'customer_id' in call_args, "Mutação detectada: filtro não aplicado"
        assert call_args['customer_id'] == 1

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_filter_key_mutation(self, mock_service):
        """
        Detecta mutação: filters['customer_id'] -> filters['car_id']

        Chaves de filtro devem corresponder aos parâmetros corretos.
        """
        mock_service.search_rentals.return_value = []

        response = client.get('/rentals/search/filter?status=active')

        # Verifica se o filtro foi passado com a chave correta
        call_args = mock_service.search_rentals.call_args[0][0]
        assert 'status' in call_args, "Mutação detectada: chave de filtro incorreta"
        assert call_args['status'] == 'active'

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_multiple_filters_mutation(self, mock_service):
        """
        Detecta mutação na aplicação de múltiplos filtros.

        Todos os filtros fornecidos devem ser aplicados.
        """
        mock_service.search_rentals.return_value = []

        response = client.get(
            '/rentals/search/filter?customer_id=1&status=active'
        )

        # Verifica se todos os filtros foram aplicados
        call_args = mock_service.search_rentals.call_args[0][0]
        assert 'customer_id' in call_args, "Mutação detectada: filtro ausente"
        assert 'status' in call_args, "Mutação detectada: filtro ausente"
        assert call_args['customer_id'] == 1
        assert call_args['status'] == 'active'


class TestRentalControllerUpdateMutations:
    """Testes para detectar mutações na lógica de atualização."""

    @patch('src.controllers.rental_controller.rental_service')
    def test_detect_none_filter_mutation_in_update(self, mock_service):
        """
        Detecta mutação: if v is not None -> if v is None

        Apenas campos não-nulos devem ser incluídos na atualização.
        """
        mock_rental = Mock(spec=Rental)
        mock_rental.to_dict.return_value = {
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'completed'
        }
        mock_service.update_rental.return_value = mock_rental

        response = client.put('/rentals/1', json={
            'status': 'completed'
        })

        # Verifica se apenas o status foi incluído na atualização
        call_args = mock_service.update_rental.call_args[0][1]
        assert 'status' in call_args, "Mutação detectada: campo não incluído"
        assert 'customer_id' not in call_args, "Mutação detectada: campo nulo incluído"
        assert 'car_id' not in call_args, "Mutação detectada: campo nulo incluído"
