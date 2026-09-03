"""Vercel ASGI entrypoint for the NexusShield FastAPI application."""

from mangum import Mangum

from backend.app.main import app

handler = Mangum(app)
