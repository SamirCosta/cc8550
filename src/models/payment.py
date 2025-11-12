from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Payment:
    """
    Modelo que representa um pagamento de aluguel.

    Attributes:
        id: Identificador único do pagamento
        rental_id: ID do aluguel relacionado
        amount: Valor do pagamento
        payment_method: Método de pagamento (credit_card, debit_card, cash, pix)
        payment_date: Data do pagamento
        status: Status do pagamento (pending, completed, failed)
        created_at: Data e hora de criação do registro
    """

    rental_id: int
    amount: float
    payment_method: str
    payment_date: datetime
    status: str = "pending"
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """
        Converte o objeto Payment para um dicionário.

        Returns:
            dict: Dicionário com os dados do pagamento
        """
        return {
            "id": self.id,
            "rental_id": self.rental_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_date": self.payment_date.isoformat() if isinstance(self.payment_date, datetime) else self.payment_date,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        """
        Cria uma instância de Payment a partir de um dicionário.

        Args:
            data: Dicionário com os dados do pagamento

        Returns:
            Payment: Instância do modelo Payment
        """
        payment_date = data["payment_date"]
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date)

        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(data["created_at"])
            else:
                created_at = data["created_at"]

        return cls(
            id=data.get("id"),
            rental_id=data["rental_id"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            payment_date=payment_date,
            status=data.get("status", "pending"),
            created_at=created_at
        )
