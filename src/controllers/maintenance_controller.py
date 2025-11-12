from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from src.services import MaintenanceService
from src.utils import RentalException, NotFoundException, ValidationException, BusinessRuleException


router = APIRouter(prefix="/maintenances", tags=["maintenances"])
maintenance_service = MaintenanceService()


class MaintenanceCreate(BaseModel):
    """Schema para criação de manutenção."""
    car_id: int = Field(..., gt=0)
    description: str = Field(..., min_length=1)
    maintenance_date: Optional[str] = None
    cost: float = Field(..., gt=0)
    status: str = "scheduled"


class MaintenanceUpdate(BaseModel):
    """Schema para atualização de manutenção."""
    car_id: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    maintenance_date: Optional[str] = None
    cost: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None


class MaintenanceResponse(BaseModel):
    """Schema de resposta para manutenção."""
    id: int
    car_id: int
    description: str
    maintenance_date: str
    cost: float
    status: str


@router.post("/", response_model=MaintenanceResponse, status_code=201)
def create_maintenance(maintenance_data: MaintenanceCreate):
    """
    Cria uma nova manutenção no sistema.

    Args:
        maintenance_data: Dados da manutenção a ser criada

    Returns:
        MaintenanceResponse: Manutenção criada

    Raises:
        HTTPException: Se houver erro na validação ou criação
    """
    try:
        maintenance = maintenance_service.create_maintenance(maintenance_data.dict())
        return maintenance.to_dict()
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(maintenance_id: int):
    """
    Busca uma manutenção pelo ID.

    Args:
        maintenance_id: ID da manutenção

    Returns:
        MaintenanceResponse: Dados da manutenção

    Raises:
        HTTPException: Se a manutenção não for encontrada
    """
    try:
        maintenance = maintenance_service.get_maintenance(maintenance_id)
        return maintenance.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[MaintenanceResponse])
def get_all_maintenances():
    """
    Lista todas as manutenções cadastradas.

    Returns:
        List[MaintenanceResponse]: Lista de manutenções
    """
    try:
        maintenances = maintenance_service.get_all_maintenances()
        return [maintenance.to_dict() for maintenance in maintenances]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/car/{car_id}", response_model=List[MaintenanceResponse])
def get_maintenances_by_car(car_id: int):
    """
    Busca manutenções de um carro específico.

    Args:
        car_id: ID do carro

    Returns:
        List[MaintenanceResponse]: Lista de manutenções do carro
    """
    try:
        maintenances = maintenance_service.get_maintenances_by_car(car_id)
        return [maintenance.to_dict() for maintenance in maintenances]
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(maintenance_id: int, maintenance_data: MaintenanceUpdate):
    """
    Atualiza uma manutenção existente.

    Args:
        maintenance_id: ID da manutenção
        maintenance_data: Dados a serem atualizados

    Returns:
        MaintenanceResponse: Manutenção atualizada

    Raises:
        HTTPException: Se houver erro na validação ou atualização
    """
    try:
        update_data = {k: v for k, v in maintenance_data.dict().items() if v is not None}
        maintenance = maintenance_service.update_maintenance(maintenance_id, update_data)
        return maintenance.to_dict()
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except (ValidationException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{maintenance_id}/complete", response_model=MaintenanceResponse)
def complete_maintenance(maintenance_id: int):
    """
    Finaliza uma manutenção, marcando o carro como disponível.

    Args:
        maintenance_id: ID da manutenção

    Returns:
        MaintenanceResponse: Manutenção finalizada

    Raises:
        HTTPException: Se houver erro ao finalizar
    """
    try:
        maintenance = maintenance_service.complete_maintenance(maintenance_id)
        return maintenance.to_dict()
    except (NotFoundException, BusinessRuleException) as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{maintenance_id}", status_code=204)
def delete_maintenance(maintenance_id: int):
    """
    Remove uma manutenção do sistema.

    Args:
        maintenance_id: ID da manutenção

    Raises:
        HTTPException: Se a manutenção não for encontrada
    """
    try:
        maintenance_service.delete_maintenance(maintenance_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except RentalException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
