"""
Routers module - API endpoints organization
"""

from .users import router as users_router
from .products import router as products_router
from .orders import router as orders_router
from .notifications import router as notifications_router

__all__ = [
    "users_router",
    "products_router", 
    "orders_router",
    "notifications_router",
]