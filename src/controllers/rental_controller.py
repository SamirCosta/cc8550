from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from src.services import RentalService
from src.utils import RentalException, NotFoundException, ValidationException, BusinessRuleException


router = APIRouter(prefix="/rentals", tags=["rentals"])
rental_service = RentalService()


class RentalCreate(BaseModel):
    """Schema para criação de aluguel."""
    customer_id: int = Field(..., gt=0)
    car_id: int = Field(..., gt=0)
    start_date: str
    end_date: str


class RentalUpdate(BaseModel):
    """Schema para atualização de aluguel."""
    customer_id: Optional[int] = Field(None, gt=0)
    car_id: Optional[int] = Field(None, gt=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None


class RentalResponse(BaseModel):
    """Schema de resposta para aluguel."""
    id: int
    customer_id: int
    car_id: int
    start_date: str
    end_date: str
    total_value: float
    status: str


@router.post("/", response_model=RentalResponse, status_code=201)
def create_rental(rental_data: RentalCreate):
    """
    Cria um novo aluguel no sistema.

    Aplica todas as regras de negócio:
    - Verifica se cliente não possui pagamento pendente
    - Verifica se carro está disponível
    - Calcula valor total com descontos progressivos

    Args:
        rental_data: Dados do aluguel a ser criado

    Returns:
        RentalResponse: Aluguel criado

    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        rental = rental_service.create_rental(rental_data.dict())
        return rental.to_dict()
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental(rental_id: int):
    """
    Busca um aluguel pelo ID.

    Args:
        rental_id: ID do aluguel

    Returns:
        RentalResponse: Dados do aluguel

    Raises:
        HTTPException: Se o aluguel não for encontrado
    """
    try:
        rental = rental_service.get_rental(rental_id)
        return rental.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[RentalResponse])
def get_all_rentals():
    """
    Lista todos os aluguéis cadastrados.

    Returns:
        List[RentalResponse]: Lista de aluguéis
    """
    try:
        rentals = rental_service.get_all_rentals()
        return [rental.to_dict() for rental in rentals]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/search/filter", response_model=List[RentalResponse])
def search_rentals(
    customer_id: Optional[int] = Query(None, description="ID do cliente"),
    status: Optional[str] = Query(None, description="Status do aluguel"),
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)")
):
    """
    Busca aluguéis com filtros opcionais.

    Args:
        customer_id: Filtro por cliente
        status: Filtro por status
        start_date: Data inicial do período
        end_date: Data final do período

    Returns:
        List[RentalResponse]: Lista de aluguéis filtrados
    """
    try:
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if status:
            filters['status'] = status
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date

        rentals = rental_service.search_rentals(filters)
        return [rental.to_dict() for rental in rentals]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.put("/{rental_id}", response_model=RentalResponse)
def update_rental(rental_id: int, rental_data: RentalUpdate):
    """
    Atualiza um aluguel existente.

    Args:
        rental_id: ID do aluguel
        rental_data: Dados a serem atualizados

    Returns:
        RentalResponse: Aluguel atualizado

    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        update_data = {k: v for k, v in rental_data.dict().items() if v is not None}
        rental = rental_service.update_rental(rental_id, update_data)
        return rental.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{rental_id}/complete", response_model=RentalResponse)
def complete_rental(rental_id: int):
    """
    Finaliza um aluguel, marcando o carro como disponível.

    Args:
        rental_id: ID do aluguel

    Returns:
        RentalResponse: Aluguel finalizado

    Raises:
        HTTPException: Se houver erro ao finalizar
    """
    try:
        rental = rental_service.complete_rental(rental_id)
        return rental.to_dict()
    except (NotFoundException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{rental_id}/cancel", response_model=RentalResponse)
def cancel_rental(rental_id: int):
    """
    Cancela um aluguel, marcando o carro como disponível.

    Args:
        rental_id: ID do aluguel

    Returns:
        RentalResponse: Aluguel cancelado

    Raises:
        HTTPException: Se houver erro ao cancelar
    """
    try:
        rental = rental_service.cancel_rental(rental_id)
        return rental.to_dict()
    except (NotFoundException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{rental_id}", status_code=204)
def delete_rental(rental_id: int):
    """
    Remove um aluguel do sistema.

    Args:
        rental_id: ID do aluguel

    Raises:
        HTTPException: Se o aluguel não for encontrado
    """
    try:
        rental_service.delete_rental(rental_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
