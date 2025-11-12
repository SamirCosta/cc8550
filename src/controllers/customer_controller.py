from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from src.services import CustomerService
from src.utils import RentalException, NotFoundException, ValidationException, BusinessRuleException


router = APIRouter(prefix="/customers", tags=["customers"])
customer_service = CustomerService()


class CustomerCreate(BaseModel):
    """Schema para criação de cliente."""
    name: str = Field(..., min_length=1, max_length=200)
    cpf: str = Field(..., min_length=11, max_length=14)
    phone: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    has_pending_payment: bool = False


class CustomerUpdate(BaseModel):
    """Schema para atualização de cliente."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    cpf: Optional[str] = Field(None, min_length=11, max_length=14)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    has_pending_payment: Optional[bool] = None


class CustomerResponse(BaseModel):
    """Schema de resposta para cliente."""
    id: int
    name: str
    cpf: str
    phone: str
    email: str
    has_pending_payment: bool


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(customer_data: CustomerCreate):
    """
    Cria um novo cliente no sistema.

    Args:
        customer_data: Dados do cliente a ser criado

    Returns:
        CustomerResponse: Cliente criado

    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        customer = customer_service.create_customer(customer_data.dict())
        return customer.to_dict()
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    """
    Busca um cliente pelo ID.

    Args:
        customer_id: ID do cliente

    Returns:
        CustomerResponse: Dados do cliente

    Raises:
        HTTPException: Se o cliente não for encontrado
    """
    try:
        customer = customer_service.get_customer(customer_id)
        return customer.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[CustomerResponse])
def get_all_customers():
    """
    Lista todos os clientes cadastrados.

    Returns:
        List[CustomerResponse]: Lista de clientes
    """
    try:
        customers = customer_service.get_all_customers()
        return [customer.to_dict() for customer in customers]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer_data: CustomerUpdate):
    """
    Atualiza um cliente existente.

    Args:
        customer_id: ID do cliente
        customer_data: Dados a serem atualizados

    Returns:
        CustomerResponse: Cliente atualizado

    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        update_data = {k: v for k, v in customer_data.dict().items() if v is not None}
        customer = customer_service.update_customer(customer_id, update_data)
        return customer.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    """
    Remove um cliente do sistema.

    Args:
        customer_id: ID do cliente

    Raises:
        HTTPException: Se o cliente não for encontrado
    """
    try:
        customer_service.delete_customer(customer_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
