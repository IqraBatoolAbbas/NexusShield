"""NexusShield application factory and top-level router."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import db, init_db
from .routes import router


def create_app() -> FastAPI:
    application = FastAPI(title="NexusShield API", version="2.0.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in os.getenv(
                "NEXUSSHIELD_ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router,prefix="/api")

    @application.on_event("startup")
    def startup() -> None:
        init_db()

    return application


app = create_app()

__all__ = ["app", "create_app", "db", "init_db"]
