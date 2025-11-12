from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Customer:
    """
    Modelo que representa um cliente no sistema de aluguel.

    Attributes:
        id: Identificador único do cliente
        name: Nome completo do cliente
        cpf: CPF do cliente
        phone: Telefone de contato
        email: Email do cliente
        has_pending_payment: Indica se o cliente possui pagamento pendente
        created_at: Data e hora de criação do registro
    """

    name: str
    cpf: str
    phone: str
    email: str
    has_pending_payment: bool = False
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Converte o objeto Customer para um dicionário.

        Returns:
            dict: Dicionário com os dados do cliente
        """
        return {
            "id": self.id,
            "name": self.name,
            "cpf": self.cpf,
            "phone": self.phone,
            "email": self.email,
            "has_pending_payment": self.has_pending_payment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """
        Cria uma instância de Customer a partir de um dicionário.

        Args:
            data: Dicionário com os dados do cliente

        Returns:
            Customer: Instância do modelo Customer
        """
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"])
            else:
                created_at = data["created_at"]

        return cls(
            id=data.get("id"),
            name=data["name"],
            cpf=data["cpf"],
            phone=data["phone"],
            email=data["email"],
            has_pending_payment=bool(data.get("has_pending_payment", False)),
            created_at=created_at
        )
