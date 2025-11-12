from typing import List, Dict, Any, Optional
from src.models import Customer
from src.repositories import CustomerRepository, PaymentRepository, RentalRepository
from src.utils import Validator, ValidationException, BusinessRuleException, setup_logger


class CustomerService:
    """
    Serviço de negócio para operações relacionadas a clientes.

    Contém a lógica de negócio e validações para gerenciamento
    de clientes, incluindo validações de CPF, email e verificação de inadimplência.
    """

    def __init__(
        self,
        customer_repository: Optional[CustomerRepository] = None,
        payment_repository: Optional[PaymentRepository] = None,
        rental_repository: Optional[RentalRepository] = None
    ) -> None:
        self.customer_repository = customer_repository or CustomerRepository()
        self.payment_repository = payment_repository or PaymentRepository()
        self.rental_repository = rental_repository or RentalRepository()
        self.logger = setup_logger()

    def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """
        Cria um novo cliente com validações.

        Args:
            customer_data: Dicionário com os dados do cliente

        Returns:
            Customer: Cliente criado

        Raises:
            ValidationException: Se os dados forem inválidos
            BusinessRuleException: Se CPF ou email já estiverem cadastrados
        """
        self.logger.info(f"Criando novo cliente: {customer_data.get('cpf')}")

        Validator.validate_cpf(customer_data['cpf'])
        Validator.validate_email(customer_data['email'])
        Validator.validate_phone(customer_data['phone'])

        existing_cpf = self.customer_repository.find_by_cpf(customer_data['cpf'])
        if existing_cpf:
            raise BusinessRuleException("CPF já cadastrado no sistema")

        existing_email = self.customer_repository.find_by_email(customer_data['email'])
        if existing_email:
            raise BusinessRuleException("Email já cadastrado no sistema")

        customer = Customer.from_dict(customer_data)
        created_customer = self.customer_repository.create(customer)

        self.logger.info(f"Cliente criado com sucesso: ID {created_customer.id}")
        return created_customer

    def get_customer(self, customer_id: int) -> Customer:
        """
        Busca um cliente pelo ID.

        Args:
            customer_id: ID do cliente

        Returns:
            Customer: Cliente encontrado
        """
        self.logger.info(f"Buscando cliente: ID {customer_id}")
        return self.customer_repository.find_by_id(customer_id)

    def get_all_customers(self) -> List[Customer]:
        """
        Busca todos os clientes.

        Returns:
            List[Customer]: Lista de clientes
        """
        self.logger.info("Buscando todos os clientes")
        return self.customer_repository.find_all()

    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Customer:
        """
        Atualiza um cliente existente.

        Args:
            customer_id: ID do cliente
            customer_data: Dicionário com os dados atualizados

        Returns:
            Customer: Cliente atualizado

        Raises:
            ValidationException: Se os dados forem inválidos
        """
        self.logger.info(f"Atualizando cliente: ID {customer_id}")

        customer = self.customer_repository.find_by_id(customer_id)

        if 'cpf' in customer_data and customer_data['cpf'] != customer.cpf:
            Validator.validate_cpf(customer_data['cpf'])
            existing = self.customer_repository.find_by_cpf(customer_data['cpf'])
            if existing:
                raise BusinessRuleException("CPF já cadastrado no sistema")

        if 'email' in customer_data and customer_data['email'] != customer.email:
            Validator.validate_email(customer_data['email'])
            existing = self.customer_repository.find_by_email(customer_data['email'])
            if existing:
                raise BusinessRuleException("Email já cadastrado no sistema")

        if 'phone' in customer_data:
            Validator.validate_phone(customer_data['phone'])

        for key, value in customer_data.items():
            if hasattr(customer, key) and key != 'id':
                setattr(customer, key, value)

        updated_customer = self.customer_repository.update(customer)
        self.logger.info(f"Cliente atualizado com sucesso: ID {customer_id}")
        return updated_customer

    def delete_customer(self, customer_id: int) -> bool:
        """
        Remove um cliente do sistema.

        Args:
            customer_id: ID do cliente

        Returns:
            bool: True se removido com sucesso
        """
        self.logger.info(f"Removendo cliente: ID {customer_id}")
        result = self.customer_repository.delete(customer_id)
        self.logger.info(f"Cliente removido com sucesso: ID {customer_id}")
        return result

    def check_payment_status(self, customer_id: int) -> bool:
        """
        Verifica se o cliente possui pagamentos pendentes.

        Regra de negócio: Cliente com pagamento pendente não pode alugar.

        Args:
            customer_id: ID do cliente

        Returns:
            bool: True se não há pagamentos pendentes

        Raises:
            BusinessRuleException: Se houver pagamento pendente
        """
        self.logger.info(f"Verificando status de pagamento do cliente: ID {customer_id}")

        rentals = self.rental_repository.find_by_customer(customer_id)

        for rental in rentals:
            pending_payments = self.payment_repository.find_pending_by_rental(rental.id)
            if pending_payments:
                self.customer_repository.update_payment_status(customer_id, True)
                raise BusinessRuleException(
                    f"Cliente possui pagamento pendente no aluguel #{rental.id}"
                )

        self.customer_repository.update_payment_status(customer_id, False)
        return True
