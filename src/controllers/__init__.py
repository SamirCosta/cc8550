from .car_controller import router as car_router
from .customer_controller import router as customer_router
from .rental_controller import router as rental_router
from .payment_controller import router as payment_router
from .maintenance_controller import router as maintenance_router

__all__ = [
    "car_router",
    "customer_router",
    "rental_router",
    "payment_router",
    "maintenance_router"
]
