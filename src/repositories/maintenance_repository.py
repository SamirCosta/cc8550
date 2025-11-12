from typing import List, Optional
from src.models import Maintenance
from src.config import Database
from src.utils import DatabaseException, NotFoundException


class MaintenanceRepository:
    """
    Repositório para operações de banco de dados relacionadas a manutenções.

    Implementa o padrão Repository para abstrair o acesso a dados
    e fornecer operações CRUD para a entidade Maintenance.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        self.db = database or Database()

    def create(self, maintenance: Maintenance) -> Maintenance:
        """
        Cria uma nova manutenção no banco de dados.

        Args:
            maintenance: Objeto Maintenance a ser criado

        Returns:
            Maintenance: Objeto Maintenance com o ID atualizado

        Raises:
            DatabaseException: Se houver erro ao criar a manutenção
        """
        try:
            query = """
                INSERT INTO maintenances (car_id, description, maintenance_date, cost, status)
                VALUES (?, ?, ?, ?, ?)
            """
            maintenance_id = self.db.execute_update(
                query,
                (maintenance.car_id, maintenance.description,
                 maintenance.maintenance_date.isoformat(), maintenance.cost, maintenance.status)
            )
            maintenance.id = maintenance_id
            return maintenance
        except Exception as e:
            raise DatabaseException(f"Erro ao criar manutenção: {str(e)}")

    def find_by_id(self, maintenance_id: int) -> Maintenance:
        """
        Busca uma manutenção pelo ID.

        Args:
            maintenance_id: ID da manutenção

        Returns:
            Maintenance: Objeto Maintenance encontrado

        Raises:
            NotFoundException: Se a manutenção não for encontrada
        """
        query = "SELECT * FROM maintenances WHERE id = ?"
        results = self.db.execute_query(query, (maintenance_id,))

        if not results:
            raise NotFoundException(f"Manutenção com ID {maintenance_id} não encontrada")

        return Maintenance.from_dict(results[0])

    def find_all(self) -> List[Maintenance]:
        """
        Busca todas as manutenções.

        Returns:
            List[Maintenance]: Lista de manutenções
        """
        query = "SELECT * FROM maintenances ORDER BY id DESC"
        results = self.db.execute_query(query)
        return [Maintenance.from_dict(row) for row in results]

    def update(self, maintenance: Maintenance) -> Maintenance:
        """
        Atualiza uma manutenção existente.

        Args:
            maintenance: Objeto Maintenance com os dados atualizados

        Returns:
            Maintenance: Objeto Maintenance atualizado

        Raises:
            NotFoundException: Se a manutenção não for encontrada
            DatabaseException: Se houver erro ao atualizar
        """
        self.find_by_id(maintenance.id)

        try:
            query = """
                UPDATE maintenances
                SET car_id = ?, description = ?, maintenance_date = ?, cost = ?, status = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (maintenance.car_id, maintenance.description,
                 maintenance.maintenance_date.isoformat(), maintenance.cost,
                 maintenance.status, maintenance.id)
            )
            return maintenance
        except Exception as e:
            raise DatabaseException(f"Erro ao atualizar manutenção: {str(e)}")

    def delete(self, maintenance_id: int) -> bool:
        """
        Remove uma manutenção do banco de dados.

        Args:
            maintenance_id: ID da manutenção a ser removida

        Returns:
            bool: True se a manutenção foi removida

        Raises:
            NotFoundException: Se a manutenção não for encontrada
        """
        self.find_by_id(maintenance_id)

        query = "DELETE FROM maintenances WHERE id = ?"
        self.db.execute_update(query, (maintenance_id,))
        return True

    def find_by_car(self, car_id: int) -> List[Maintenance]:
        """
        Busca manutenções de um carro específico.

        Args:
            car_id: ID do carro

        Returns:
            List[Maintenance]: Lista de manutenções do carro
        """
        query = "SELECT * FROM maintenances WHERE car_id = ? ORDER BY maintenance_date DESC"
        results = self.db.execute_query(query, (car_id,))
        return [Maintenance.from_dict(row) for row in results]

    def find_active_by_car(self, car_id: int) -> List[Maintenance]:
        """
        Busca manutenções ativas (agendadas ou em progresso) de um carro.

        Args:
            car_id: ID do carro

        Returns:
            List[Maintenance]: Lista de manutenções ativas
        """
        query = """
            SELECT * FROM maintenances
            WHERE car_id = ? AND status IN ('scheduled', 'in_progress')
            ORDER BY maintenance_date DESC
        """
        results = self.db.execute_query(query, (car_id,))
        return [Maintenance.from_dict(row) for row in results]

    def update_status(self, maintenance_id: int, status: str) -> bool:
        """
        Atualiza o status de uma manutenção.

        Args:
            maintenance_id: ID da manutenção
            status: Novo status da manutenção

        Returns:
            bool: True se atualizado com sucesso

        Raises:
            NotFoundException: Se a manutenção não for encontrada
        """
        self.find_by_id(maintenance_id)

        query = "UPDATE maintenances SET status = ? WHERE id = ?"
        self.db.execute_update(query, (status, maintenance_id))
        return True
