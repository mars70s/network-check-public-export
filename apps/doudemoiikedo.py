"""doudemoiikedo.com ASGI composition root."""

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from apps.composition import create_network_check_app


def create_app() -> FastAPI:
    """Build the current doudemoiikedo.com application without changing its routes."""

    return create_network_check_app()


app = create_app()
