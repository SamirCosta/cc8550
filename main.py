from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.config import Database, settings
from src.controllers import (
    car_router,
    customer_router,
    rental_router,
    payment_router,
    maintenance_router
)
from src.utils import setup_logger, RentalException


logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.

    Inicializa o banco de dados na inicialização
    e realiza limpeza no encerramento.
    """
    logger.info("Inicializando aplicação")
    db = Database()
    db.initialize_schema()
    logger.info("Schema do banco de dados inicializado")
    yield
    logger.info("Encerrando aplicação")


app = FastAPI(
    title="Car Rental API",
    description="API REST para sistema de aluguel de carros",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(RentalException)
async def rental_exception_handler(request: Request, exc: RentalException):
    """
    Handler global para exceções personalizadas do sistema.

    Args:
        request: Request HTTP
        exc: Exceção capturada

    Returns:
        JSONResponse: Resposta formatada com erro
    """
    logger.error(f"Erro: {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"detail": exc.message}
    )


@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raiz da API.

    Returns:
        dict: Informações básicas da API
    """
    return {
        "message": "Car Rental API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Endpoint de health check.

    Returns:
        dict: Status da aplicação
    """
    return {"status": "healthy"}


app.include_router(car_router)
app.include_router(customer_router)
app.include_router(rental_router)
app.include_router(payment_router)
app.include_router(maintenance_router)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando servidor em {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
