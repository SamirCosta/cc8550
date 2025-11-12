from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Rental:
    """
    Modelo que representa um aluguel de carro.

    Attributes:
        id: Identificador único do aluguel
        customer_id: ID do cliente que realizou o aluguel
        car_id: ID do carro alugado
        start_date: Data de início do aluguel
        end_date: Data de término do aluguel
        total_value: Valor total do aluguel
        status: Status do aluguel (active, completed, cancelled)
        created_at: Data e hora de criação do registro
    """

    customer_id: int
    car_id: int
    start_date: datetime
    end_date: datetime
    total_value: float
    status: str = "active"
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Converte o objeto Rental para um dicionário.

        Returns:
            dict: Dicionário com os dados do aluguel
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "car_id": self.car_id,
            "start_date": self.start_date.isoformat() if isinstance(self.start_date, datetime) else self.start_date,
            "end_date": self.end_date.isoformat() if isinstance(self.end_date, datetime) else self.end_date,
            "total_value": self.total_value,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Rental':
        """
        Cria uma instância de Rental a partir de um dicionário.

        Args:
            data: Dicionário com os dados do aluguel

        Returns:
            Rental: Instância do modelo Rental
        """
        start_date = data["start_date"]
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        end_date = data["end_date"]
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"])
            else:
                created_at = data["created_at"]

        return cls(
            id=data.get("id"),
            customer_id=data["customer_id"],
            car_id=data["car_id"],
            start_date=start_date,
            end_date=end_date,
            total_value=data["total_value"],
            status=data.get("status", "active"),
            created_at=created_at
        )
