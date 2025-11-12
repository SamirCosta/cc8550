from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from src.services import PaymentService
from src.utils import RentalException, NotFoundException, ValidationException, BusinessRuleException


router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()


class PaymentCreate(BaseModel):
    """Schema para criação de pagamento."""
    rental_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)
    payment_date: Optional[str] = None
    status: str = "pending"


class PaymentUpdate(BaseModel):
    """Schema para atualização de pagamento."""
    rental_id: Optional[int] = Field(None, gt=0)
    amount: Optional[float] = Field(None, gt=0)
    payment_method: Optional[str] = None
    payment_date: Optional[str] = None
    status: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema de resposta para pagamento."""
    id: int
    rental_id: int
    amount: float
    payment_method: str
    payment_date: str
    status: str


@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(payment_data: PaymentCreate):
    """
    Cria um novo pagamento no sistema.

    Args:
        payment_data: Dados do pagamento a ser criado

    Returns:
        PaymentResponse: Pagamento criado

    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        payment = payment_service.create_payment(payment_data.dict())
        return payment.to_dict()
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int):
    """
    Busca um pagamento pelo ID.

    Args:
        payment_id: ID do pagamento

    Returns:
        PaymentResponse: Dados do pagamento

    Raises:
        HTTPException: Se o pagamento não for encontrado
    """
    try:
        payment = payment_service.get_payment(payment_id)
        return payment.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[PaymentResponse])
def get_all_payments():
    """
    Lista todos os pagamentos cadastrados.

    Returns:
        List[PaymentResponse]: Lista de pagamentos
    """
    try:
        payments = payment_service.get_all_payments()
        return [payment.to_dict() for payment in payments]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/rental/{rental_id}", response_model=List[PaymentResponse])
def get_payments_by_rental(rental_id: int):
    """
    Busca pagamentos de um aluguel específico.

    Args:
        rental_id: ID do aluguel

    Returns:
        List[PaymentResponse]: Lista de pagamentos do aluguel
    """
    try:
        payments = payment_service.get_payments_by_rental(rental_id)
        return [payment.to_dict() for payment in payments]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment_data: PaymentUpdate):
    """
    Atualiza um pagamento existente.

    Args:
        payment_id: ID do pagamento
        payment_data: Dados a serem atualizados

    Returns:
        PaymentResponse: Pagamento atualizado

    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        update_data = {k: v for k, v in payment_data.dict().items() if v is not None}
        payment = payment_service.update_payment(payment_id, update_data)
        return payment.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{payment_id}/process", response_model=PaymentResponse)
def process_payment(payment_id: int):
    """
    Processa um pagamento pendente, marcando como completado.

    Args:
        payment_id: ID do pagamento

    Returns:
        PaymentResponse: Pagamento processado

    Raises:
        HTTPException: Se houver erro ao processar
    """
    try:
        payment = payment_service.process_payment(payment_id)
        return payment.to_dict()
    except (NotFoundException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: int):
    """
    Remove um pagamento do sistema.

    Args:
        payment_id: ID do pagamento

    Raises:
        HTTPException: Se o pagamento não for encontrado
    """
    try:
        payment_service.delete_payment(payment_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
