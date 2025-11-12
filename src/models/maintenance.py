from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Maintenance:
    """
    Modelo que representa uma manutenção de carro.

    Attributes:
        id: Identificador único da manutenção
        car_id: ID do carro em manutenção
        description: Descrição da manutenção
        maintenance_date: Data da manutenção
        cost: Custo da manutenção
        status: Status da manutenção (scheduled, in_progress, completed)
        created_at: Data e hora de criação do registro
    """

    car_id: int
    description: str
    maintenance_date: datetime
    cost: float
    status: str = "scheduled"
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Converte o objeto Maintenance para um dicionário.

        Returns:
            dict: Dicionário com os dados da manutenção
        """
        return {
            "id": self.id,
            "car_id": self.car_id,
            "description": self.description,
            "maintenance_date": self.maintenance_date.isoformat() if isinstance(self.maintenance_date, datetime) else self.maintenance_date,
            "cost": self.cost,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Maintenance':
        """
        Cria uma instância de Maintenance a partir de um dicionário.

        Args:
            data: Dicionário com os dados da manutenção

        Returns:
            Maintenance: Instância do modelo Maintenance
        """
        maintenance_date = data["maintenance_date"]
        if isinstance(maintenance_date, str):
            maintenance_date = datetime.fromisoformat(maintenance_date)

        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"])
            else:
                created_at = data["created_at"]

        return cls(
            id=data.get("id"),
            car_id=data["car_id"],
            description=data["description"],
            maintenance_date=maintenance_date,
            cost=data["cost"],
            status=data.get("status", "scheduled"),
            created_at=created_at
        )
