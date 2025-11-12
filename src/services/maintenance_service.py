from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Maintenance
from src.repositories import MaintenanceRepository, CarRepository
from src.utils import Validator, ValidationException, BusinessRuleException, setup_logger


class MaintenanceService:
    """
    Serviço de negócio para operações relacionadas a manutenções.

    Contém a lógica de negócio para agendamento e gerenciamento
    de manutenções de carros.
    """

    def __init__(
        self,
        maintenance_repository: Optional[MaintenanceRepository] = None,
        car_repository: Optional[CarRepository] = None
    ) -> None:
        self.maintenance_repository = maintenance_repository or MaintenanceRepository()
        self.car_repository = car_repository or CarRepository()
        self.logger = setup_logger()

    def create_maintenance(self, maintenance_data: Dict[str, Any]) -> Maintenance:
        """
        Cria uma nova manutenção com validações.

        Args:
            maintenance_data: Dicionário com os dados da manutenção

        Returns:
            Maintenance: Manutenção criada

        Raises:
            ValidationException: Se os dados forem inválidos
            BusinessRuleException: Se o carro não existir
        """
        self.logger.info(f"Criando manutenção para carro {maintenance_data.get('car_id')}")

        self.car_repository.find_by_id(maintenance_data['car_id'])

        Validator.validate_positive_number(maintenance_data['cost'], "Custo da manutenção")

        maintenance_date = maintenance_data.get('maintenance_date', datetime.now())
        if isinstance(maintenance_date, str):
            maintenance_date = datetime.fromisoformat(maintenance_date)

        maintenance = Maintenance(
            car_id=maintenance_data['car_id'],
            description=maintenance_data['description'],
            maintenance_date=maintenance_date,
            cost=maintenance_data['cost'],
            status=maintenance_data.get('status', 'scheduled')
        )

        created_maintenance = self.maintenance_repository.create(maintenance)

        if created_maintenance.status in ['scheduled', 'in_progress']:
            self.car_repository.update_availability(maintenance_data['car_id'], False)

        self.logger.info(f"Manutenção criada com sucesso: ID {created_maintenance.id}")
        return created_maintenance

    def get_maintenance(self, maintenance_id: int) -> Maintenance:
        """
        Busca uma manutenção pelo ID.

        Args:
            maintenance_id: ID da manutenção

        Returns:
            Maintenance: Manutenção encontrada
        """
        self.logger.info(f"Buscando manutenção: ID {maintenance_id}")
        return self.maintenance_repository.find_by_id(maintenance_id)

    def get_all_maintenances(self) -> List[Maintenance]:
        """
        Busca todas as manutenções.

        Returns:
            List[Maintenance]: Lista de manutenções
        """
        self.logger.info("Buscando todas as manutenções")
        return self.maintenance_repository.find_all()

    def get_maintenances_by_car(self, car_id: int) -> List[Maintenance]:
        """
        Busca manutenções de um carro específico.

        Args:
            car_id: ID do carro

        Returns:
            List[Maintenance]: Lista de manutenções
        """
        self.logger.info(f"Buscando manutenções do carro: ID {car_id}")
        return self.maintenance_repository.find_by_car(car_id)

    def update_maintenance(self, maintenance_id: int, maintenance_data: Dict[str, Any]) -> Maintenance:
        """
        Atualiza uma manutenção existente.

        Args:
            maintenance_id: ID da manutenção
            maintenance_data: Dicionário com os dados atualizados

        Returns:
            Maintenance: Manutenção atualizada
        """
        self.logger.info(f"Atualizando manutenção: ID {maintenance_id}")

        maintenance = self.maintenance_repository.find_by_id(maintenance_id)

        if 'cost' in maintenance_data:
            Validator.validate_positive_number(maintenance_data['cost'], "Custo da manutenção")

        for key, value in maintenance_data.items():
            if hasattr(maintenance, key) and key != 'id':
                setattr(maintenance, key, value)

        updated_maintenance = self.maintenance_repository.update(maintenance)
        self.logger.info(f"Manutenção atualizada com sucesso: ID {maintenance_id}")
        return updated_maintenance

    def complete_maintenance(self, maintenance_id: int) -> Maintenance:
        """
        Finaliza uma manutenção, marcando o carro como disponível.

        Args:
            maintenance_id: ID da manutenção

        Returns:
            Maintenance: Manutenção finalizada
        """
        self.logger.info(f"Finalizando manutenção: ID {maintenance_id}")

        maintenance = self.maintenance_repository.find_by_id(maintenance_id)

        if maintenance.status == 'completed':
            raise BusinessRuleException("Manutenção já foi finalizada")

        self.maintenance_repository.update_status(maintenance_id, 'completed')

        active_maintenances = self.maintenance_repository.find_active_by_car(maintenance.car_id)
        if not active_maintenances:
            self.car_repository.update_availability(maintenance.car_id, True)

        self.logger.info(f"Manutenção finalizada com sucesso: ID {maintenance_id}")
        return self.maintenance_repository.find_by_id(maintenance_id)

    def delete_maintenance(self, maintenance_id: int) -> bool:
        """
        Remove uma manutenção do sistema.

        Args:
            maintenance_id: ID da manutenção

        Returns:
            bool: True se removido com sucesso
        """
        self.logger.info(f"Removendo manutenção: ID {maintenance_id}")
        result = self.maintenance_repository.delete(maintenance_id)
        self.logger.info(f"Manutenção removida com sucesso: ID {maintenance_id}")
        return result
