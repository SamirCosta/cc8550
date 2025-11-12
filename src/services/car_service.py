from typing import List, Optional, Dict, Any
from src.models import Car
from src.repositories import CarRepository, MaintenanceRepository
from src.utils import Validator, ValidationException, BusinessRuleException, setup_logger


class CarService:
    """
    Serviço de negócio para operações relacionadas a carros.

    Contém a lógica de negócio e validações para gerenciamento
    de carros, incluindo validações de dados e regras de negócio.
    """

    def __init__(
        self,
        car_repository: Optional[CarRepository] = None,
        maintenance_repository: Optional[MaintenanceRepository] = None
    ) -> None:
        self.car_repository = car_repository or CarRepository()
        self.maintenance_repository = maintenance_repository or MaintenanceRepository()
        self.logger = setup_logger()

    def create_car(self, car_data: Dict[str, Any]) -> Car:
        """
        Cria um novo carro com validações.

        Args:
            car_data: Dicionário com os dados do carro

        Returns:
            Car: Carro criado

        Raises:
            ValidationException: Se os dados forem inválidos
            BusinessRuleException: Se a placa já estiver cadastrada
        """
        self.logger.info(f"Criando novo carro: {car_data.get('license_plate')}")

        Validator.validate_license_plate(car_data['license_plate'])
        Validator.validate_positive_number(car_data['daily_rate'], "Valor da diária")
        Validator.validate_year(car_data['year'])

        existing_car = self.car_repository.find_by_license_plate(car_data['license_plate'])
        if existing_car:
            raise BusinessRuleException("Placa já cadastrada no sistema")

        car = Car.from_dict(car_data)
        created_car = self.car_repository.create(car)

        self.logger.info(f"Carro criado com sucesso: ID {created_car.id}")
        return created_car

    def get_car(self, car_id: int) -> Car:
        """
        Busca um carro pelo ID.

        Args:
            car_id: ID do carro

        Returns:
            Car: Carro encontrado
        """
        self.logger.info(f"Buscando carro: ID {car_id}")
        return self.car_repository.find_by_id(car_id)

    def get_all_cars(self) -> List[Car]:
        """
        Busca todos os carros.

        Returns:
            List[Car]: Lista de carros
        """
        self.logger.info("Buscando todos os carros")
        return self.car_repository.find_all()

    def get_available_cars(self, filters: Optional[Dict[str, Any]] = None) -> List[Car]:
        """
        Busca carros disponíveis com filtros opcionais.

        Args:
            filters: Filtros de busca (brand, model, max_price, min_year, max_year)

        Returns:
            List[Car]: Lista de carros disponíveis
        """
        self.logger.info(f"Buscando carros disponíveis com filtros: {filters}")
        return self.car_repository.find_available(filters)

    def update_car(self, car_id: int, car_data: Dict[str, Any]) -> Car:
        """
        Atualiza um carro existente.

        Args:
            car_id: ID do carro
            car_data: Dicionário com os dados atualizados

        Returns:
            Car: Carro atualizado

        Raises:
            ValidationException: Se os dados forem inválidos
        """
        self.logger.info(f"Atualizando carro: ID {car_id}")

        car = self.car_repository.find_by_id(car_id)

        if 'license_plate' in car_data and car_data['license_plate'] != car.license_plate:
            Validator.validate_license_plate(car_data['license_plate'])
            existing = self.car_repository.find_by_license_plate(car_data['license_plate'])
            if existing:
                raise BusinessRuleException("Placa já cadastrada no sistema")

        if 'daily_rate' in car_data:
            Validator.validate_positive_number(car_data['daily_rate'], "Valor da diária")

        if 'year' in car_data:
            Validator.validate_year(car_data['year'])

        for key, value in car_data.items():
            if hasattr(car, key):
                setattr(car, key, value)

        updated_car = self.car_repository.update(car)
        self.logger.info(f"Carro atualizado com sucesso: ID {car_id}")
        return updated_car

    def delete_car(self, car_id: int) -> bool:
        """
        Remove um carro do sistema.

        Args:
            car_id: ID do carro

        Returns:
            bool: True se removido com sucesso
        """
        self.logger.info(f"Removendo carro: ID {car_id}")
        result = self.car_repository.delete(car_id)
        self.logger.info(f"Carro removido com sucesso: ID {car_id}")
        return result

    def check_availability(self, car_id: int) -> bool:
        """
        Verifica se um carro está disponível para aluguel.

        Regra de negócio: Um carro está disponível se:
        1. O campo is_available está True
        2. Não possui manutenção ativa (scheduled ou in_progress)

        Args:
            car_id: ID do carro

        Returns:
            bool: True se o carro está disponível

        Raises:
            BusinessRuleException: Se o carro não estiver disponível
        """
        self.logger.info(f"Verificando disponibilidade do carro: ID {car_id}")

        car = self.car_repository.find_by_id(car_id)

        if not car.is_available:
            raise BusinessRuleException("Carro não está disponível para aluguel")

        active_maintenances = self.maintenance_repository.find_active_by_car(car_id)
        if active_maintenances:
            raise BusinessRuleException("Carro possui manutenção ativa ou agendada")

        return True
