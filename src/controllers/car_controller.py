from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from src.services import CarService
from src.utils import RentalException, NotFoundException, ValidationException, BusinessRuleException


router = APIRouter(prefix="/cars", tags=["cars"])
car_service = CarService()


class CarCreate(BaseModel):
    """Schema para criação de carro."""
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900)
    license_plate: str = Field(..., min_length=7, max_length=8)
    daily_rate: float = Field(..., gt=0)
    is_available: bool = True


class CarUpdate(BaseModel):
    """Schema para atualização de carro."""
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900)
    license_plate: Optional[str] = Field(None, min_length=7, max_length=8)
    daily_rate: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None


class CarResponse(BaseModel):
    """Schema de resposta para carro."""
    id: int
    brand: str
    model: str
    year: int
    license_plate: str
    daily_rate: float
    is_available: bool


@router.post("/", response_model=CarResponse, status_code=201)
def create_car(car_data: CarCreate):
    """
    Cria um novo carro no sistema.

    Args:
        car_data: Dados do carro a ser criado

    Returns:
        CarResponse: Carro criado

    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        car = car_service.create_car(car_data.dict())
        return car.to_dict()
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int):
    """
    Busca um carro pelo ID.

    Args:
        car_id: ID do carro

    Returns:
        CarResponse: Dados do carro

    Raises:
        HTTPException: Se o carro não for encontrado
    """
    try:
        car = car_service.get_car(car_id)
        return car.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[CarResponse])
def get_all_cars():
    """
    Lista todos os carros cadastrados.

    Returns:
        List[CarResponse]: Lista de carros
    """
    try:
        cars = car_service.get_all_cars()
        return [car.to_dict() for car in cars]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/available/search", response_model=List[CarResponse])
def search_available_cars(
    brand: Optional[str] = Query(None, description="Marca do carro"),
    model: Optional[str] = Query(None, description="Modelo do carro"),
    max_price: Optional[float] = Query(None, description="Preço máximo da diária"),
    min_year: Optional[int] = Query(None, description="Ano mínimo"),
    max_year: Optional[int] = Query(None, description="Ano máximo")
):
    """
    Busca carros disponíveis com filtros opcionais.

    Args:
        brand: Filtro por marca
        model: Filtro por modelo
        max_price: Preço máximo da diária
        min_year: Ano mínimo
        max_year: Ano máximo

    Returns:
        List[CarResponse]: Lista de carros disponíveis
    """
    try:
        filters = {}
        if brand:
            filters['brand'] = brand
        if model:
            filters['model'] = model
        if max_price:
            filters['max_price'] = max_price
        if min_year:
            filters['min_year'] = min_year
        if max_year:
            filters['max_year'] = max_year

        cars = car_service.get_available_cars(filters)
        return [car.to_dict() for car in cars]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_data: CarUpdate):
    """
    Atualiza um carro existente.

    Args:
        car_id: ID do carro
        car_data: Dados a serem atualizados

    Returns:
        CarResponse: Carro atualizado

    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        update_data = {k: v for k, v in car_data.dict().items() if v is not None}
        car = car_service.update_car(car_id, update_data)
        return car.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int):
    """
    Remove um carro do sistema.

    Args:
        car_id: ID do carro

    Raises:
        HTTPException: Se o carro não for encontrado
    """
    try:
        car_service.delete_car(car_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
