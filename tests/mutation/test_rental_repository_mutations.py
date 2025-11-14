"""
Testes de mutação para RentalRepository.

Este módulo contém testes essenciais para detectar mutações críticas no código
do RentalRepository.

Categorias de mutação testadas:
1. Queries SQL (INSERT, UPDATE, DELETE, SELECT)
2. Cláusulas WHERE
3. ORDER BY
4. Tratamento de exceções
5. Conversões de dados
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from src.repositories.rental_repository import RentalRepository
from src.models import Rental
from src.utils import DatabaseException, NotFoundException


class TestRentalRepositoryCriticalMutations:
    """Testes essenciais para detectar mutações críticas."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_insert_column_mutation(self):
        """Detecta mutação: remoção de colunas no INSERT"""
        rental = Rental(
            customer_id=1, car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0, status='active'
        )

        self.repo.db.execute_update.return_value = 1
        result = self.repo.create(rental)

        call_args = self.repo.db.execute_update.call_args[0]
        query = call_args[0]
        values = call_args[1]

        assert 'customer_id' in query, "Mutação detectada: coluna customer_id ausente"
        assert 'total_value' in query, "Mutação detectada: coluna total_value ausente"
        assert len(values) == 6, "Mutação detectada: número de valores incorreto"

    def test_detect_delete_where_clause_mutation(self):
        """Detecta mutação: DELETE FROM rentals WHERE id = ? -> DELETE FROM rentals"""
        self.repo.db.execute_query.return_value = [{
            'id': 1, 'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05',
            'total_value': 500.0, 'status': 'active'
        }]

        self.repo.delete(1)

        call_args = self.repo.db.execute_update.call_args[0]
        query = call_args[0]
        params = call_args[1]

        assert 'WHERE' in query, "Mutação detectada: cláusula WHERE ausente"
        assert params[0] == 1, "Mutação detectada: parâmetro incorreto"

    def test_detect_where_clause_addition_mutation_in_filters(self):
        """Detecta mutação: remoção de condições WHERE em filtros"""
        self.repo.db.execute_query.return_value = []

        filters = {
            'customer_id': 1,
            'status': 'active',
            'start_date': '2025-01-01'
        }

        self.repo.find_with_filters(filters)

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]
        params = call_args[1]

        assert 'customer_id = ?' in query, "Mutação detectada: filtro customer_id ausente"
        assert 'status = ?' in query, "Mutação detectada: filtro status ausente"
        assert len(params) == 3, "Mutação detectada: número de parâmetros incorreto"

    def test_detect_order_by_direction_mutation_in_find_all(self):
        """Detecta mutação: ORDER BY id DESC -> ORDER BY id ASC"""
        self.repo.db.execute_query.return_value = [
            {'id': 3, 'customer_id': 1, 'car_id': 1, 'start_date': '2025-01-15',
             'end_date': '2025-01-20', 'total_value': 500.0, 'status': 'active'},
            {'id': 2, 'customer_id': 1, 'car_id': 1, 'start_date': '2025-01-10',
             'end_date': '2025-01-15', 'total_value': 500.0, 'status': 'active'}
        ]

        results = self.repo.find_all()

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        assert 'ORDER BY' in query, "Mutação detectada: ORDER BY ausente"
        assert 'DESC' in query, "Mutação detectada: direção de ordenação incorreta"
        assert results[0].id == 3, "Mutação detectada: ordenação incorreta"

    def test_detect_not_found_exception_mutation_in_find_by_id(self):
        """Detecta mutação: raise NotFoundException -> raise DatabaseException"""
        self.repo.db.execute_query.return_value = []

        with pytest.raises(NotFoundException, match="não encontrado"):
            self.repo.find_by_id(999)

    def test_detect_database_exception_mutation_in_create(self):
        """Detecta mutação: raise DatabaseException -> pass ou outro tipo"""
        self.repo.db.execute_update.side_effect = Exception("Erro de banco")

        rental = Rental(
            customer_id=1, car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0, status='active'
        )

        with pytest.raises(DatabaseException, match="Erro ao criar aluguel"):
            self.repo.create(rental)

    def test_detect_from_dict_mutation_in_find_by_id(self):
        """Detecta mutação: Rental.from_dict(results[0]) -> results[0]"""
        self.repo.db.execute_query.return_value = [{
            'id': 1, 'customer_id': 1, 'car_id': 1,
            'start_date': '2025-01-01', 'end_date': '2025-01-05',
            'total_value': 500.0, 'status': 'active'
        }]

        result = self.repo.find_by_id(1)

        assert isinstance(result, Rental), "Mutação detectada: conversão para Rental ausente"
        assert result.id == 1, "Mutação detectada: dados não mapeados corretamente"
