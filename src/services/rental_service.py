from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Rental
from src.repositories import RentalRepository, CarRepository, CustomerRepository
from src.services import CarService, CustomerService
from src.utils import Validator, ValidationException, BusinessRuleException, setup_logger


class RentalService:
    """
    Serviço de negócio para operações relacionadas a aluguéis.

    Contém a lógica de negócio mais complexa do sistema, incluindo
    cálculo de valores com descontos, validações de disponibilidade
    e gerenciamento do ciclo de vida dos aluguéis.
    """

    def __init__(
        self,
        rental_repository: Optional[RentalRepository] = None,
        car_repository: Optional[CarRepository] = None,
        customer_repository: Optional[CustomerRepository] = None,
        car_service: Optional[CarService] = None,
        customer_service: Optional[CustomerService] = None
    ) -> None:
        self.rental_repository = rental_repository or RentalRepository()
        self.car_repository = car_repository or CarRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.car_service = car_service or CarService()
        self.customer_service = customer_service or CustomerService()
        self.logger = setup_logger()

    def calculate_rental_value(self, car_id: int, start_date: datetime, end_date: datetime) -> float:
        """
        Calcula o valor total do aluguel com descontos progressivos.

        Regra de negócio complexa:
        - 1-7 dias: valor integral
        - 8-14 dias: 10% de desconto
        - 15-30 dias: 15% de desconto
        - Acima de 30 dias: 20% de desconto

        Args:
            car_id: ID do carro
            start_date: Data de início
            end_date: Data de término

        Returns:
            float: Valor total calculado

        Raises:
            ValidationException: Se as datas forem inválidas
        """
        self.logger.info(f"Calculando valor do aluguel para carro ID {car_id}")

        Validator.validate_date_range(start_date, end_date)

        car = self.car_repository.find_by_id(car_id)
        days = (end_date - start_date).days

        if days <= 0:
            raise ValidationException("Período do aluguel deve ser de pelo menos 1 dia")

        base_value = car.daily_rate * days
        discount = 0.0

        if days > 30:
            discount = 0.20
        elif days >= 15:
            discount = 0.15
        elif days >= 8:
            discount = 0.10

        total_value = base_value * (1 - discount)

        self.logger.info(
            f"Valor calculado: R$ {total_value:.2f} "
            f"({days} dias, desconto de {discount*100}%)"
        )

        return round(total_value, 2)

    def create_rental(self, rental_data: Dict[str, Any]) -> Rental:
        """
        Cria um novo aluguel com todas as validações de negócio.

        Regras aplicadas:
        1. Verifica se o cliente não possui pagamentos pendentes
        2. Verifica se o carro está disponível
        3. Calcula o valor total com descontos
        4. Marca o carro como indisponível

        Args:
            rental_data: Dicionário com os dados do aluguel

        Returns:
            Rental: Aluguel criado

        Raises:
            BusinessRuleException: Se alguma regra de negócio for violada
        """
        self.logger.info(
            f"Criando aluguel para cliente {rental_data.get('customer_id')} "
            f"e carro {rental_data.get('car_id')}"
        )

        customer_id = rental_data['customer_id']
        car_id = rental_data['car_id']

        self.customer_service.check_payment_status(customer_id)
        self.car_service.check_availability(car_id)

        start_date = rental_data['start_date']
        end_date = rental_data['end_date']

        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        total_value = self.calculate_rental_value(car_id, start_date, end_date)

        rental = Rental(
            customer_id=customer_id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            total_value=total_value,
            status="active"
        )

        created_rental = self.rental_repository.create(rental)
        self.car_repository.update_availability(car_id, False)

        self.logger.info(f"Aluguel criado com sucesso: ID {created_rental.id}")
        return created_rental

    def get_rental(self, rental_id: int) -> Rental:
        """
        Busca um aluguel pelo ID.

        Args:
            rental_id: ID do aluguel

        Returns:
            Rental: Aluguel encontrado
        """
        self.logger.info(f"Buscando aluguel: ID {rental_id}")
        return self.rental_repository.find_by_id(rental_id)

    def get_all_rentals(self) -> List[Rental]:
        """
        Busca todos os aluguéis.

        Returns:
            List[Rental]: Lista de aluguéis
        """
        self.logger.info("Buscando todos os aluguéis")
        return self.rental_repository.find_all()

    def search_rentals(self, filters: Dict[str, Any]) -> List[Rental]:
        """
        Busca aluguéis com filtros (customer_id, status, período).

        Args:
            filters: Filtros de busca

        Returns:
            List[Rental]: Lista de aluguéis filtrados
        """
        self.logger.info(f"Buscando aluguéis com filtros: {filters}")
        return self.rental_repository.find_with_filters(filters)

    def update_rental(self, rental_id: int, rental_data: Dict[str, Any]) -> Rental:
        """
        Atualiza um aluguel existente.

        Args:
            rental_id: ID do aluguel
            rental_data: Dicionário com os dados atualizados

        Returns:
            Rental: Aluguel atualizado
        """
        self.logger.info(f"Atualizando aluguel: ID {rental_id}")

        rental = self.rental_repository.find_by_id(rental_id)

        if 'start_date' in rental_data or 'end_date' in rental_data:
            start = rental_data.get('start_date', rental.start_date)
            end = rental_data.get('end_date', rental.end_date)

            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)

            new_value = self.calculate_rental_value(rental.car_id, start, end)
            rental_data['total_value'] = new_value

        for key, value in rental_data.items():
            if hasattr(rental, key) and key != 'id':
                setattr(rental, key, value)

        updated_rental = self.rental_repository.update(rental)
        self.logger.info(f"Aluguel atualizado com sucesso: ID {rental_id}")
        return updated_rental

    def complete_rental(self, rental_id: int) -> Rental:
        """
        Finaliza um aluguel, marcando o carro como disponível novamente.

        Args:
            rental_id: ID do aluguel

        Returns:
            Rental: Aluguel finalizado
        """
        self.logger.info(f"Finalizando aluguel: ID {rental_id}")

        rental = self.rental_repository.find_by_id(rental_id)

        if rental.status != 'active':
            raise BusinessRuleException("Apenas aluguéis ativos podem ser finalizados")

        self.rental_repository.update_status(rental_id, 'completed')
        self.car_repository.update_availability(rental.car_id, True)

        self.logger.info(f"Aluguel finalizado com sucesso: ID {rental_id}")
        return self.rental_repository.find_by_id(rental_id)

    def cancel_rental(self, rental_id: int) -> Rental:
        """
        Cancela um aluguel, marcando o carro como disponível novamente.

        Args:
            rental_id: ID do aluguel

        Returns:
            Rental: Aluguel cancelado
        """
        self.logger.info(f"Cancelando aluguel: ID {rental_id}")

        rental = self.rental_repository.find_by_id(rental_id)

        if rental.status != 'active':
            raise BusinessRuleException("Apenas aluguéis ativos podem ser cancelados")

        self.rental_repository.update_status(rental_id, 'cancelled')
        self.car_repository.update_availability(rental.car_id, True)

        self.logger.info(f"Aluguel cancelado com sucesso: ID {rental_id}")
        return self.rental_repository.find_by_id(rental_id)

    def delete_rental(self, rental_id: int) -> bool:
        """
        Remove um aluguel do sistema.

        Args:
            rental_id: ID do aluguel

        Returns:
            bool: True se removido com sucesso
        """
        self.logger.info(f"Removendo aluguel: ID {rental_id}")
        result = self.rental_repository.delete(rental_id)
        self.logger.info(f"Aluguel removido com sucesso: ID {rental_id}")
        return result
