from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models import Rental
from src.config import Database
from src.utils import DatabaseException, NotFoundException


class RentalRepository:
    """
    Repositório para operações de banco de dados relacionadas a aluguéis.

    Implementa o padrão Repository para abstrair o acesso a dados
    e fornecer operações CRUD para a entidade Rental.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        self.db = database or Database()

    def create(self, rental: Rental) -> Rental:
        """
        Cria um novo aluguel no banco de dados.

        Args:
            rental: Objeto Rental a ser criado

        Returns:
            Rental: Objeto Rental com o ID atualizado

        Raises:
            DatabaseException: Se houver erro ao criar o aluguel
        """
        try:
            query = """
                INSERT INTO rentals (customer_id, car_id, start_date, end_date, total_value, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            rental_id = self.db.execute_update(
                query,
                (rental.customer_id, rental.car_id,
                 rental.start_date.isoformat(), rental.end_date.isoformat(),
                 rental.total_value, rental.status)
            )
            rental.id = rental_id
            return rental
        except Exception as e:
            raise DatabaseException(f"Erro ao criar aluguel: {str(e)}")

    def find_by_id(self, rental_id: int) -> Rental:
        """
        Busca um aluguel pelo ID.

        Args:
            rental_id: ID do aluguel

        Returns:
            Rental: Objeto Rental encontrado

        Raises:
            NotFoundException: Se o aluguel não for encontrado
        """
        query = "SELECT * FROM rentals WHERE id = ?"
        results = self.db.execute_query(query, (rental_id,))

        if not results:
            raise NotFoundException(f"Aluguel com ID {rental_id} não encontrado")

        return Rental.from_dict(results[0])

    def find_all(self) -> List[Rental]:
        """
        Busca todos os aluguéis.

        Returns:
            List[Rental]: Lista de aluguéis
        """
        query = "SELECT * FROM rentals ORDER BY id DESC"
        results = self.db.execute_query(query)
        return [Rental.from_dict(row) for row in results]

    def update(self, rental: Rental) -> Rental:
        """
        Atualiza um aluguel existente.

        Args:
            rental: Objeto Rental com os dados atualizados

        Returns:
            Rental: Objeto Rental atualizado

        Raises:
            NotFoundException: Se o aluguel não for encontrado
            DatabaseException: Se houver erro ao atualizar
        """
        self.find_by_id(rental.id)

        try:
            query = """
                UPDATE rentals
                SET customer_id = ?, car_id = ?, start_date = ?, end_date = ?,
                    total_value = ?, status = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (rental.customer_id, rental.car_id,
                 rental.start_date.isoformat(), rental.end_date.isoformat(),
                 rental.total_value, rental.status, rental.id)
            )
            return rental
        except Exception as e:
            raise DatabaseException(f"Erro ao atualizar aluguel: {str(e)}")

    def delete(self, rental_id: int) -> bool:
        """
        Remove um aluguel do banco de dados.

        Args:
            rental_id: ID do aluguel a ser removido

        Returns:
            bool: True se o aluguel foi removido

        Raises:
            NotFoundException: Se o aluguel não for encontrado
        """
        self.find_by_id(rental_id)

        query = "DELETE FROM rentals WHERE id = ?"
        self.db.execute_update(query, (rental_id,))
        return True

    def find_by_customer(self, customer_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Rental]:
        """
        Busca aluguéis de um cliente específico com filtros opcionais.

        Args:
            customer_id: ID do cliente
            filters: Dicionário com filtros (status, start_date, end_date)

        Returns:
            List[Rental]: Lista de aluguéis do cliente
        """
        query = "SELECT * FROM rentals WHERE customer_id = ?"
        params = [customer_id]

        if filters:
            if filters.get("status"):
                query += " AND status = ?"
                params.append(filters["status"])

            if filters.get("start_date"):
                query += " AND start_date >= ?"
                params.append(filters["start_date"])

            if filters.get("end_date"):
                query += " AND end_date <= ?"
                params.append(filters["end_date"])

        query += " ORDER BY start_date DESC"
        results = self.db.execute_query(query, tuple(params))
        return [Rental.from_dict(row) for row in results]

    def find_by_car(self, car_id: int) -> List[Rental]:
        """
        Busca aluguéis de um carro específico.

        Args:
            car_id: ID do carro

        Returns:
            List[Rental]: Lista de aluguéis do carro
        """
        query = "SELECT * FROM rentals WHERE car_id = ? ORDER BY start_date DESC"
        results = self.db.execute_query(query, (car_id,))
        return [Rental.from_dict(row) for row in results]

    def find_active_by_car(self, car_id: int) -> Optional[Rental]:
        """
        Busca aluguel ativo de um carro específico.

        Args:
            car_id: ID do carro

        Returns:
            Optional[Rental]: Aluguel ativo se encontrado, None caso contrário
        """
        query = "SELECT * FROM rentals WHERE car_id = ? AND status = 'active' LIMIT 1"
        results = self.db.execute_query(query, (car_id,))

        if not results:
            return None

        return Rental.from_dict(results[0])

    def update_status(self, rental_id: int, status: str) -> bool:
        """
        Atualiza o status de um aluguel.

        Args:
            rental_id: ID do aluguel
            status: Novo status do aluguel

        Returns:
            bool: True se atualizado com sucesso

        Raises:
            NotFoundException: Se o aluguel não for encontrado
        """
        self.find_by_id(rental_id)

        query = "UPDATE rentals SET status = ? WHERE id = ?"
        self.db.execute_update(query, (status, rental_id))
        return True

    def find_with_filters(self, filters: Dict[str, Any]) -> List[Rental]:
        """
        Busca aluguéis com múltiplos filtros.

        Args:
            filters: Dicionário com filtros (customer_id, status, start_date, end_date)

        Returns:
            List[Rental]: Lista de aluguéis filtrados
        """
        query = "SELECT * FROM rentals WHERE 1=1"
        params = []

        if filters.get("customer_id"):
            query += " AND customer_id = ?"
            params.append(filters["customer_id"])

        if filters.get("status"):
            query += " AND status = ?"
            params.append(filters["status"])

        if filters.get("start_date"):
            query += " AND start_date >= ?"
            params.append(filters["start_date"])

        if filters.get("end_date"):
            query += " AND end_date <= ?"
            params.append(filters["end_date"])

        query += " ORDER BY start_date DESC"
        results = self.db.execute_query(query, tuple(params))
        return [Rental.from_dict(row) for row in results]
