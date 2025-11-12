from typing import List, Optional
from src.models import Customer
from src.config import Database
from src.utils import DatabaseException, NotFoundException


class CustomerRepository:
    """
    Repositório para operações de banco de dados relacionadas a clientes.

    Implementa o padrão Repository para abstrair o acesso a dados
    e fornecer operações CRUD para a entidade Customer.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        self.db = database or Database()

    def create(self, customer: Customer) -> Customer:
        """
        Cria um novo cliente no banco de dados.

        Args:
            customer: Objeto Customer a ser criado

        Returns:
            Customer: Objeto Customer com o ID atualizado

        Raises:
            DatabaseException: Se houver erro ao criar o cliente
        """
        try:
            query = """
                INSERT INTO customers (name, cpf, phone, email, has_pending_payment)
                VALUES (?, ?, ?, ?, ?)
            """
            customer_id = self.db.execute_update(
                query,
                (customer.name, customer.cpf, customer.phone, customer.email,
                 int(customer.has_pending_payment))
            )
            customer.id = customer_id
            return customer
        except Exception as e:
            raise DatabaseException(f"Erro ao criar cliente: {str(e)}")

    def find_by_id(self, customer_id: int) -> Customer:
        """
        Busca um cliente pelo ID.

        Args:
            customer_id: ID do cliente

        Returns:
            Customer: Objeto Customer encontrado

        Raises:
            NotFoundException: Se o cliente não for encontrado
        """
        query = "SELECT * FROM customers WHERE id = ?"
        results = self.db.execute_query(query, (customer_id,))

        if not results:
            raise NotFoundException(f"Cliente com ID {customer_id} não encontrado")

        return Customer.from_dict(results[0])

    def find_all(self) -> List[Customer]:
        """
        Busca todos os clientes.

        Returns:
            List[Customer]: Lista de clientes
        """
        query = "SELECT * FROM customers ORDER BY id DESC"
        results = self.db.execute_query(query)
        return [Customer.from_dict(row) for row in results]

    def update(self, customer: Customer) -> Customer:
        """
        Atualiza um cliente existente.

        Args:
            customer: Objeto Customer com os dados atualizados

        Returns:
            Customer: Objeto Customer atualizado

        Raises:
            NotFoundException: Se o cliente não for encontrado
            DatabaseException: Se houver erro ao atualizar
        """
        self.find_by_id(customer.id)

        try:
            query = """
                UPDATE customers
                SET name = ?, cpf = ?, phone = ?, email = ?, has_pending_payment = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (customer.name, customer.cpf, customer.phone, customer.email,
                 int(customer.has_pending_payment), customer.id)
            )
            return customer
        except Exception as e:
            raise DatabaseException(f"Erro ao atualizar cliente: {str(e)}")

    def delete(self, customer_id: int) -> bool:
        """
        Remove um cliente do banco de dados.

        Args:
            customer_id: ID do cliente a ser removido

        Returns:
            bool: True se o cliente foi removido

        Raises:
            NotFoundException: Se o cliente não for encontrado
        """
        self.find_by_id(customer_id)

        query = "DELETE FROM customers WHERE id = ?"
        self.db.execute_update(query, (customer_id,))
        return True

    def find_by_cpf(self, cpf: str) -> Optional[Customer]:
        """
        Busca um cliente pelo CPF.

        Args:
            cpf: CPF do cliente

        Returns:
            Optional[Customer]: Objeto Customer se encontrado, None caso contrário
        """
        query = "SELECT * FROM customers WHERE cpf = ?"
        results = self.db.execute_query(query, (cpf,))

        if not results:
            return None

        return Customer.from_dict(results[0])

    def update_payment_status(self, customer_id: int, has_pending: bool) -> bool:
        """
        Atualiza o status de pagamento pendente de um cliente.

        Args:
            customer_id: ID do cliente
            has_pending: Indica se há pagamento pendente

        Returns:
            bool: True se atualizado com sucesso

        Raises:
            NotFoundException: Se o cliente não for encontrado
        """
        self.find_by_id(customer_id)

        query = "UPDATE customers SET has_pending_payment = ? WHERE id = ?"
        self.db.execute_update(query, (int(has_pending), customer_id))
        return True

    def find_by_email(self, email: str) -> Optional[Customer]:
        """
        Busca um cliente pelo email.

        Args:
            email: Email do cliente

        Returns:
            Optional[Customer]: Objeto Customer se encontrado, None caso contrário
        """
        query = "SELECT * FROM customers WHERE email = ?"
        results = self.db.execute_query(query, (email,))

        if not results:
            return None

        return Customer.from_dict(results[0])
