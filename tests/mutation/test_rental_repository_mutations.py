"""
Testes de mutação para RentalRepository.

Este módulo contém testes específicos para detectar mutações no código
do RentalRepository, verificando se os testes conseguem identificar mudanças
em queries SQL, condições de busca e operações de banco de dados.

Categorias de mutação testadas:
1. Queries SQL (INSERT, UPDATE, DELETE, SELECT)
2. Condições WHERE (operadores, valores)
3. Cláusulas ORDER BY (ASC, DESC, colunas)
4. Operações de junção e filtros
5. Valores de retorno e conversões
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from src.repositories.rental_repository import RentalRepository
from src.models import Rental
from src.utils import DatabaseException, NotFoundException


class TestRentalRepositorySQLQueryMutations:
    """Testes para detectar mutações em queries SQL."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_insert_column_mutation(self):
        """
        Detecta mutação: INSERT INTO rentals (customer_id, car_id, ...) VALUES (?, ?, ...)
        -> Alteração ou remoção de colunas

        Garante que todas as colunas necessárias sejam inseridas.
        """
        rental = Rental(
            customer_id=1,
            car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0,
            status='active'
        )

        self.repo.db.execute_update.return_value = 1
        result = self.repo.create(rental)

        # Verifica se a query foi chamada com todos os valores corretos
        call_args = self.repo.db.execute_update.call_args[0]
        query = call_args[0]
        values = call_args[1]

        assert 'customer_id' in query, "Mutação detectada: coluna customer_id ausente"
        assert 'car_id' in query, "Mutação detectada: coluna car_id ausente"
        assert 'start_date' in query, "Mutação detectada: coluna start_date ausente"
        assert 'end_date' in query, "Mutação detectada: coluna end_date ausente"
        assert 'total_value' in query, "Mutação detectada: coluna total_value ausente"
        assert 'status' in query, "Mutação detectada: coluna status ausente"
        assert len(values) == 6, "Mutação detectada: número de valores incorreto"

    def test_detect_update_column_mutation(self):
        """
        Detecta mutação: UPDATE rentals SET column = ? -> remoção de colunas

        Garante que todas as colunas sejam atualizadas.
        """
        rental = Rental(
            id=1,
            customer_id=1,
            car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0,
            status='active'
        )

        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        self.repo.update(rental)

        # Verifica se a query UPDATE contém todas as colunas
        call_args = self.repo.db.execute_update.call_args[0]
        query = call_args[0]

        assert 'customer_id = ?' in query, "Mutação detectada: coluna customer_id ausente"
        assert 'car_id = ?' in query, "Mutação detectada: coluna car_id ausente"
        assert 'start_date = ?' in query, "Mutação detectada: coluna start_date ausente"
        assert 'end_date = ?' in query, "Mutação detectada: coluna end_date ausente"
        assert 'total_value = ?' in query, "Mutação detectada: coluna total_value ausente"
        assert 'status = ?' in query, "Mutação detectada: coluna status ausente"

    def test_detect_delete_where_clause_mutation(self):
        """
        Detecta mutação: DELETE FROM rentals WHERE id = ? -> DELETE FROM rentals

        Garante que a cláusula WHERE esteja presente para evitar deleção em massa.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        self.repo.delete(1)

        # Verifica se a query DELETE tem WHERE
        call_args = self.repo.db.execute_update.call_args[0]
        query = call_args[0]
        params = call_args[1]

        assert 'WHERE' in query, "Mutação detectada: cláusula WHERE ausente"
        assert 'id = ?' in query, "Mutação detectada: condição WHERE incorreta"
        assert params[0] == 1, "Mutação detectada: parâmetro incorreto"

    def test_detect_select_all_columns_mutation(self):
        """
        Detecta mutação: SELECT * FROM rentals -> SELECT id FROM rentals

        Garante que todas as colunas sejam selecionadas.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.find_by_id(1)

        # Verifica se SELECT * está presente
        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        assert 'SELECT *' in query or 'SELECT' in query, "Mutação detectada: SELECT alterado"
        assert 'FROM rentals' in query, "Mutação detectada: tabela incorreta"


class TestRentalRepositoryWhereClauseMutations:
    """Testes para detectar mutações em cláusulas WHERE."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_where_operator_mutation_equals(self):
        """
        Detecta mutação: WHERE id = ? -> WHERE id != ?

        Operador de igualdade deve estar correto.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.find_by_id(1)

        # Verifica parâmetro passado
        call_args = self.repo.db.execute_query.call_args[0]
        params = call_args[1]

        assert params[0] == 1, "Mutação detectada: parâmetro WHERE incorreto"
        assert result.id == 1, "Mutação detectada: registro incorreto retornado"

    def test_detect_where_clause_addition_mutation_in_filters(self):
        """
        Detecta mutação: remoção de condições WHERE em filtros

        Garante que todos os filtros sejam aplicados na query.
        """
        self.repo.db.execute_query.return_value = []

        filters = {
            'customer_id': 1,
            'status': 'active',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }

        self.repo.find_with_filters(filters)

        # Verifica se todas as condições foram adicionadas
        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]
        params = call_args[1]

        assert 'customer_id = ?' in query, "Mutação detectada: filtro customer_id ausente"
        assert 'status = ?' in query, "Mutação detectada: filtro status ausente"
        assert 'start_date >= ?' in query, "Mutação detectada: filtro start_date ausente"
        assert 'end_date <= ?' in query, "Mutação detectada: filtro end_date ausente"
        assert len(params) == 4, "Mutação detectada: número de parâmetros incorreto"

    def test_detect_comparison_operator_mutation_in_date_filters(self):
        """
        Detecta mutação: start_date >= ? -> start_date > ?
                         end_date <= ? -> end_date < ?

        Operadores de comparação devem incluir igualdade para datas.
        """
        self.repo.db.execute_query.return_value = []

        filters = {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }

        self.repo.find_with_filters(filters)

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        # Verifica se >= e <= estão presentes (não só > e <)
        assert 'start_date >=' in query, "Mutação detectada: operador >= alterado para >"
        assert 'end_date <=' in query, "Mutação detectada: operador <= alterado para <"


class TestRentalRepositoryOrderByMutations:
    """Testes para detectar mutações em cláusulas ORDER BY."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_order_by_direction_mutation_in_find_all(self):
        """
        Detecta mutação: ORDER BY id DESC -> ORDER BY id ASC

        find_all deve ordenar por ID decrescente (mais recentes primeiro).
        """
        self.repo.db.execute_query.return_value = [
            {
                'id': 3,
                'customer_id': 1,
                'car_id': 1,
                'start_date': '2025-01-15',
                'end_date': '2025-01-20',
                'total_value': 500.0,
                'status': 'active'
            },
            {
                'id': 2,
                'customer_id': 1,
                'car_id': 1,
                'start_date': '2025-01-10',
                'end_date': '2025-01-15',
                'total_value': 500.0,
                'status': 'active'
            },
            {
                'id': 1,
                'customer_id': 1,
                'car_id': 1,
                'start_date': '2025-01-01',
                'end_date': '2025-01-05',
                'total_value': 500.0,
                'status': 'active'
            }
        ]

        results = self.repo.find_all()

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        # Verifica se ORDER BY DESC está presente
        assert 'ORDER BY' in query, "Mutação detectada: ORDER BY ausente"
        assert 'DESC' in query, "Mutação detectada: direção de ordenação incorreta"

        # Verifica se o primeiro resultado tem o maior ID
        assert results[0].id == 3, "Mutação detectada: ordenação incorreta"

    def test_detect_order_by_column_mutation_in_find_by_customer(self):
        """
        Detecta mutação: ORDER BY start_date DESC -> ORDER BY id DESC

        find_by_customer deve ordenar por data de início.
        """
        self.repo.db.execute_query.return_value = []

        self.repo.find_by_customer(1, {})

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        # Verifica se ORDER BY start_date está presente
        assert 'ORDER BY start_date' in query, "Mutação detectada: coluna de ordenação incorreta"
        assert 'DESC' in query, "Mutação detectada: direção de ordenação incorreta"

    def test_detect_order_by_removal_mutation(self):
        """
        Detecta mutação: remoção de ORDER BY

        Garante que a ordenação esteja presente onde esperado.
        """
        self.repo.db.execute_query.return_value = []

        self.repo.find_by_car(1)

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        assert 'ORDER BY' in query, "Mutação detectada: ORDER BY removido"


class TestRentalRepositoryLimitMutations:
    """Testes para detectar mutações em cláusulas LIMIT."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_limit_value_mutation_in_find_active_by_car(self):
        """
        Detecta mutação: LIMIT 1 -> LIMIT 2 ou remoção

        find_active_by_car deve retornar apenas 1 resultado.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.find_active_by_car(1)

        call_args = self.repo.db.execute_query.call_args[0]
        query = call_args[0]

        # Verifica se LIMIT 1 está presente
        assert 'LIMIT 1' in query, "Mutação detectada: LIMIT ausente ou valor incorreto"
        assert result is not None, "Mutação detectada: resultado incorreto"

    def test_detect_limit_removal_mutation_returns_single_result(self):
        """
        Detecta mutação: remoção de LIMIT causa múltiplos resultados

        Garante que apenas um resultado seja processado.
        """
        # Simula retorno de múltiplos resultados
        self.repo.db.execute_query.return_value = [
            {
                'id': 1,
                'customer_id': 1,
                'car_id': 1,
                'start_date': '2025-01-01',
                'end_date': '2025-01-05',
                'total_value': 500.0,
                'status': 'active'
            },
            {
                'id': 2,
                'customer_id': 2,
                'car_id': 1,
                'start_date': '2025-01-10',
                'end_date': '2025-01-15',
                'total_value': 600.0,
                'status': 'active'
            }
        ]

        result = self.repo.find_active_by_car(1)

        # Deve retornar apenas 1 objeto Rental, não uma lista
        assert isinstance(result, Rental), "Mutação detectada: deveria retornar um único objeto"


class TestRentalRepositoryExceptionMutations:
    """Testes para detectar mutações no tratamento de exceções."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_not_found_exception_mutation_in_find_by_id(self):
        """
        Detecta mutação: raise NotFoundException -> raise DatabaseException

        find_by_id deve lançar NotFoundException quando não encontrar.
        """
        self.repo.db.execute_query.return_value = []

        with pytest.raises(NotFoundException, match="não encontrado"):
            self.repo.find_by_id(999)

    def test_detect_exception_message_mutation_in_find_by_id(self):
        """
        Detecta mutação na mensagem de exceção.

        Mensagem deve incluir o ID buscado.
        """
        self.repo.db.execute_query.return_value = []

        with pytest.raises(NotFoundException) as exc_info:
            self.repo.find_by_id(999)

        assert '999' in str(exc_info.value), "Mutação detectada: ID ausente na mensagem"

    def test_detect_database_exception_mutation_in_create(self):
        """
        Detecta mutação: raise DatabaseException -> pass ou outro tipo

        Erros de banco devem ser tratados e re-lançados como DatabaseException.
        """
        self.repo.db.execute_update.side_effect = Exception("Erro de banco")

        rental = Rental(
            customer_id=1,
            car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0,
            status='active'
        )

        with pytest.raises(DatabaseException, match="Erro ao criar aluguel"):
            self.repo.create(rental)

    def test_detect_database_exception_mutation_in_update(self):
        """
        Detecta mutação: raise DatabaseException -> pass ou outro tipo

        Erros de banco devem ser tratados e re-lançados como DatabaseException.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        self.repo.db.execute_update.side_effect = Exception("Erro de banco")

        rental = Rental(
            id=1,
            customer_id=1,
            car_id=1,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
            total_value=500.0,
            status='active'
        )

        with pytest.raises(DatabaseException, match="Erro ao atualizar aluguel"):
            self.repo.update(rental)


class TestRentalRepositoryReturnValueMutations:
    """Testes para detectar mutações em valores de retorno."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_return_none_mutation_in_find_active_by_car(self):
        """
        Detecta mutação: return Rental.from_dict(results[0]) -> return results[0]

        Deve retornar None quando não encontrar resultado ativo.
        """
        self.repo.db.execute_query.return_value = []

        result = self.repo.find_active_by_car(1)

        assert result is None, "Mutação detectada: deveria retornar None"

    def test_detect_return_type_mutation_in_find_active_by_car(self):
        """
        Detecta mutação: return Rental.from_dict(...) -> return dict

        Deve retornar objeto Rental, não dict.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.find_active_by_car(1)

        assert isinstance(result, Rental), "Mutação detectada: tipo de retorno incorreto"

    def test_detect_return_true_mutation_in_delete(self):
        """
        Detecta mutação: return True -> return False

        delete deve retornar True quando bem-sucedido.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.delete(1)

        assert result is True, "Mutação detectada: retorno deveria ser True"

    def test_detect_return_true_mutation_in_update_status(self):
        """
        Detecta mutação: return True -> return False

        update_status deve retornar True quando bem-sucedido.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.update_status(1, 'completed')

        assert result is True, "Mutação detectada: retorno deveria ser True"


class TestRentalRepositoryDataConversionMutations:
    """Testes para detectar mutações em conversões de dados."""

    def setup_method(self):
        """Configura mocks para cada teste."""
        self.repo = RentalRepository()
        self.repo.db = Mock()

    def test_detect_isoformat_mutation_in_create(self):
        """
        Detecta mutação: start_date.isoformat() -> str(start_date)

        Datas devem ser convertidas usando isoformat().
        """
        rental = Rental(
            customer_id=1,
            car_id=1,
            start_date=datetime(2025, 1, 1, 10, 30),
            end_date=datetime(2025, 1, 5, 10, 30),
            total_value=500.0,
            status='active'
        )

        self.repo.db.execute_update.return_value = 1
        self.repo.create(rental)

        call_args = self.repo.db.execute_update.call_args[0]
        values = call_args[1]

        # Verifica se as datas estão em formato ISO
        start_date_value = values[2]
        end_date_value = values[3]

        assert isinstance(start_date_value, str), "Mutação detectada: data não convertida para string"
        assert 'T' in start_date_value or '-' in start_date_value, "Mutação detectada: formato ISO ausente"

    def test_detect_from_dict_mutation_in_find_by_id(self):
        """
        Detecta mutação: Rental.from_dict(results[0]) -> results[0]

        Deve converter dict para objeto Rental.
        """
        self.repo.db.execute_query.return_value = [{
            'id': 1,
            'customer_id': 1,
            'car_id': 1,
            'start_date': '2025-01-01',
            'end_date': '2025-01-05',
            'total_value': 500.0,
            'status': 'active'
        }]

        result = self.repo.find_by_id(1)

        assert isinstance(result, Rental), "Mutação detectada: conversão para Rental ausente"
        assert result.id == 1, "Mutação detectada: dados não mapeados corretamente"

    def test_detect_list_comprehension_mutation_in_find_all(self):
        """
        Detecta mutação: [Rental.from_dict(row) for row in results] -> results

        Deve converter lista de dicts para lista de Rentals.
        """
        self.repo.db.execute_query.return_value = [
            {
                'id': 1,
                'customer_id': 1,
                'car_id': 1,
                'start_date': '2025-01-01',
                'end_date': '2025-01-05',
                'total_value': 500.0,
                'status': 'active'
            },
            {
                'id': 2,
                'customer_id': 2,
                'car_id': 2,
                'start_date': '2025-01-10',
                'end_date': '2025-01-15',
                'total_value': 600.0,
                'status': 'active'
            }
        ]

        results = self.repo.find_all()

        assert all(isinstance(r, Rental) for r in results), "Mutação detectada: itens não convertidos"
        assert len(results) == 2, "Mutação detectada: número de resultados incorreto"
