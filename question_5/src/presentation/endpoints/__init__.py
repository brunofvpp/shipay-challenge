from fastapi import APIRouter

from .health import health_router
from .users import users_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(users_router)


__all__ = ["api_v1_router"]
