from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Payment
from src.repositories import PaymentRepository, RentalRepository, CustomerRepository
from src.utils import Validator, ValidationException, BusinessRuleException, setup_logger


class PaymentService:
    """
    Serviço de negócio para operações relacionadas a pagamentos.

    Contém a lógica de negócio para processamento de pagamentos,
    validações e atualização de status de clientes.
    """

    VALID_PAYMENT_METHODS = ['credit_card', 'debit_card', 'cash', 'pix']

    def __init__(
        self,
        payment_repository: Optional[PaymentRepository] = None,
        rental_repository: Optional[RentalRepository] = None,
        customer_repository: Optional[CustomerRepository] = None
    ) -> None:
        self.payment_repository = payment_repository or PaymentRepository()
        self.rental_repository = rental_repository or RentalRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.logger = setup_logger()

    def create_payment(self, payment_data: Dict[str, Any]) -> Payment:
        """
        Cria um novo pagamento com validações.

        Args:
            payment_data: Dicionário com os dados do pagamento

        Returns:
            Payment: Pagamento criado

        Raises:
            ValidationException: Se os dados forem inválidos
            BusinessRuleException: Se o aluguel não existir
        """
        self.logger.info(f"Criando pagamento para aluguel {payment_data.get('rental_id')}")

        rental = self.rental_repository.find_by_id(payment_data['rental_id'])

        if payment_data['payment_method'] not in self.VALID_PAYMENT_METHODS:
            raise ValidationException(
                f"Método de pagamento inválido. Opções: {', '.join(self.VALID_PAYMENT_METHODS)}"
            )

        Validator.validate_positive_number(payment_data['amount'], "Valor do pagamento")

        payment_date = payment_data.get('payment_date', datetime.now())
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date)

        payment = Payment(
            rental_id=payment_data['rental_id'],
            amount=payment_data['amount'],
            payment_method=payment_data['payment_method'],
            payment_date=payment_date,
            status=payment_data.get('status', 'pending')
        )

        created_payment = self.payment_repository.create(payment)

        if created_payment.status == 'completed':
            self._update_customer_payment_status(rental.customer_id)

        self.logger.info(f"Pagamento criado com sucesso: ID {created_payment.id}")
        return created_payment

    def get_payment(self, payment_id: int) -> Payment:
        """
        Busca um pagamento pelo ID.

        Args:
            payment_id: ID do pagamento

        Returns:
            Payment: Pagamento encontrado
        """
        self.logger.info(f"Buscando pagamento: ID {payment_id}")
        return self.payment_repository.find_by_id(payment_id)

    def get_all_payments(self) -> List[Payment]:
        """
        Busca todos os pagamentos.

        Returns:
            List[Payment]: Lista de pagamentos
        """
        self.logger.info("Buscando todos os pagamentos")
        return self.payment_repository.find_all()

    def get_payments_by_rental(self, rental_id: int) -> List[Payment]:
        """
        Busca pagamentos de um aluguel específico.

        Args:
            rental_id: ID do aluguel

        Returns:
            List[Payment]: Lista de pagamentos
        """
        self.logger.info(f"Buscando pagamentos do aluguel: ID {rental_id}")
        return self.payment_repository.find_by_rental(rental_id)

    def update_payment(self, payment_id: int, payment_data: Dict[str, Any]) -> Payment:
        """
        Atualiza um pagamento existente.

        Args:
            payment_id: ID do pagamento
            payment_data: Dicionário com os dados atualizados

        Returns:
            Payment: Pagamento atualizado
        """
        self.logger.info(f"Atualizando pagamento: ID {payment_id}")

        payment = self.payment_repository.find_by_id(payment_id)

        if 'payment_method' in payment_data:
            if payment_data['payment_method'] not in self.VALID_PAYMENT_METHODS:
                raise ValidationException(
                    f"Método de pagamento inválido. Opções: {', '.join(self.VALID_PAYMENT_METHODS)}"
                )

        if 'amount' in payment_data:
            Validator.validate_positive_number(payment_data['amount'], "Valor do pagamento")

        for key, value in payment_data.items():
            if hasattr(payment, key) and key != 'id':
                setattr(payment, key, value)

        updated_payment = self.payment_repository.update(payment)

        if updated_payment.status == 'completed':
            rental = self.rental_repository.find_by_id(updated_payment.rental_id)
            self._update_customer_payment_status(rental.customer_id)

        self.logger.info(f"Pagamento atualizado com sucesso: ID {payment_id}")
        return updated_payment

    def process_payment(self, payment_id: int) -> Payment:
        """
        Processa um pagamento pendente, marcando como completado.

        Args:
            payment_id: ID do pagamento

        Returns:
            Payment: Pagamento processado
        """
        self.logger.info(f"Processando pagamento: ID {payment_id}")

        payment = self.payment_repository.find_by_id(payment_id)

        if payment.status != 'pending':
            raise BusinessRuleException("Apenas pagamentos pendentes podem ser processados")

        self.payment_repository.update_status(payment_id, 'completed')

        rental = self.rental_repository.find_by_id(payment.rental_id)
        self._update_customer_payment_status(rental.customer_id)

        self.logger.info(f"Pagamento processado com sucesso: ID {payment_id}")
        return self.payment_repository.find_by_id(payment_id)

    def delete_payment(self, payment_id: int) -> bool:
        """
        Remove um pagamento do sistema.

        Args:
            payment_id: ID do pagamento

        Returns:
            bool: True se removido com sucesso
        """
        self.logger.info(f"Removendo pagamento: ID {payment_id}")
        result = self.payment_repository.delete(payment_id)
        self.logger.info(f"Pagamento removido com sucesso: ID {payment_id}")
        return result

    def _update_customer_payment_status(self, customer_id: int) -> None:
        """
        Atualiza o status de pagamento pendente do cliente.

        Args:
            customer_id: ID do cliente
        """
        rentals = self.rental_repository.find_by_customer(customer_id)
        has_pending = False

        for rental in rentals:
            pending_payments = self.payment_repository.find_pending_by_rental(rental.id)
            if pending_payments:
                has_pending = True
                break

        self.customer_repository.update_payment_status(customer_id, has_pending)
