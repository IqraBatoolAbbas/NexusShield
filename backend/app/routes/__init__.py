"""API router assembly."""

from fastapi import APIRouter

from . import analytics, auth, shield

router = APIRouter()
router.include_router(auth.router)
router.include_router(shield.router)
router.include_router(analytics.router)

__all__ = ["router"]
