from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Car:
    """
    Modelo que representa um carro no sistema de aluguel.

    Attributes:
        id: Identificador único do carro
        brand: Marca do carro
        model: Modelo do carro
        year: Ano de fabricação
        license_plate: Placa do veículo
        daily_rate: Valor da diária de aluguel
        is_available: Indica se o carro está disponível para aluguel
        created_at: Data e hora de criação do registro
    """

    brand: str
    model: str
    year: int
    license_plate: str
    daily_rate: float
    is_available: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Converte o objeto Car para um dicionário.

        Returns:
            dict: Dicionário com os dados do carro
        """
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "license_plate": self.license_plate,
            "daily_rate": self.daily_rate,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Car':
        """
        Cria uma instância de Car a partir de um dicionário.

        Args:
            data: Dicionário com os dados do carro

        Returns:
            Car: Instância do modelo Car
        """
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"])
            else:
                created_at = data["created_at"]

        return cls(
            id=data.get("id"),
            brand=data["brand"],
            model=data["model"],
            year=data["year"],
            license_plate=data["license_plate"],
            daily_rate=data["daily_rate"],
            is_available=bool(data.get("is_available", True)),
            created_at=created_at
        )
