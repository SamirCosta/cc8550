from typing import List, Optional
from src.models import Payment
from src.config import Database
from src.utils import DatabaseException, NotFoundException


class PaymentRepository:
    """
    Repositório para operações de banco de dados relacionadas a pagamentos.

    Implementa o padrão Repository para abstrair o acesso a dados
    e fornecer operações CRUD para a entidade Payment.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        self.db = database or Database()

    def create(self, payment: Payment) -> Payment:
        """
        Cria um novo pagamento no banco de dados.

        Args:
            payment: Objeto Payment a ser criado

        Returns:
            Payment: Objeto Payment com o ID atualizado

        Raises:
            DatabaseException: Se houver erro ao criar o pagamento
        """
        try:
            query = """
                INSERT INTO payments (rental_id, amount, payment_method, payment_date, status)
                VALUES (?, ?, ?, ?, ?)
            """
            payment_id = self.db.execute_update(
                query,
                (payment.rental_id, payment.amount, payment.payment_method,
                 payment.payment_date.isoformat(), payment.status)
            )
            payment.id = payment_id
            return payment
        except Exception as e:
            raise DatabaseException(f"Erro ao criar pagamento: {str(e)}")

    def find_by_id(self, payment_id: int) -> Payment:
        """
        Busca um pagamento pelo ID.

        Args:
            payment_id: ID do pagamento

        Returns:
            Payment: Objeto Payment encontrado

        Raises:
            NotFoundException: Se o pagamento não for encontrado
        """
        query = "SELECT * FROM payments WHERE id = ?"
        results = self.db.execute_query(query, (payment_id,))

        if not results:
            raise NotFoundException(f"Pagamento com ID {payment_id} não encontrado")

        return Payment.from_dict(results[0])

    def find_all(self) -> List[Payment]:
        """
        Busca todos os pagamentos.

        Returns:
            List[Payment]: Lista de pagamentos
        """
        query = "SELECT * FROM payments ORDER BY id DESC"
        results = self.db.execute_query(query)
        return [Payment.from_dict(row) for row in results]

    def update(self, payment: Payment) -> Payment:
        """
        Atualiza um pagamento existente.

        Args:
            payment: Objeto Payment com os dados atualizados

        Returns:
            Payment: Objeto Payment atualizado

        Raises:
            NotFoundException: Se o pagamento não for encontrado
            DatabaseException: Se houver erro ao atualizar
        """
        self.find_by_id(payment.id)

        try:
            query = """
                UPDATE payments
                SET rental_id = ?, amount = ?, payment_method = ?,
                    payment_date = ?, status = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (payment.rental_id, payment.amount, payment.payment_method,
                 payment.payment_date.isoformat(), payment.status, payment.id)
            )
            return payment
        except Exception as e:
            raise DatabaseException(f"Erro ao atualizar pagamento: {str(e)}")

    def delete(self, payment_id: int) -> bool:
        """
        Remove um pagamento do banco de dados.

        Args:
            payment_id: ID do pagamento a ser removido

        Returns:
            bool: True se o pagamento foi removido

        Raises:
            NotFoundException: Se o pagamento não for encontrado
        """
        self.find_by_id(payment_id)

        query = "DELETE FROM payments WHERE id = ?"
        self.db.execute_update(query, (payment_id,))
        return True

    def find_by_rental(self, rental_id: int) -> List[Payment]:
        """
        Busca pagamentos de um aluguel específico.

        Args:
            rental_id: ID do aluguel

        Returns:
            List[Payment]: Lista de pagamentos do aluguel
        """
        query = "SELECT * FROM payments WHERE rental_id = ? ORDER BY payment_date DESC"
        results = self.db.execute_query(query, (rental_id,))
        return [Payment.from_dict(row) for row in results]

    def find_pending_by_rental(self, rental_id: int) -> List[Payment]:
        """
        Busca pagamentos pendentes de um aluguel específico.

        Args:
            rental_id: ID do aluguel

        Returns:
            List[Payment]: Lista de pagamentos pendentes
        """
        query = """
            SELECT * FROM payments
            WHERE rental_id = ? AND status = 'pending'
            ORDER BY payment_date DESC
        """
        results = self.db.execute_query(query, (rental_id,))
        return [Payment.from_dict(row) for row in results]

    def update_status(self, payment_id: int, status: str) -> bool:
        """
        Atualiza o status de um pagamento.

        Args:
            payment_id: ID do pagamento
            status: Novo status do pagamento

        Returns:
            bool: True se atualizado com sucesso

        Raises:
            NotFoundException: Se o pagamento não for encontrado
        """
        self.find_by_id(payment_id)

        query = "UPDATE payments SET status = ? WHERE id = ?"
        self.db.execute_update(query, (status, payment_id))
        return True
