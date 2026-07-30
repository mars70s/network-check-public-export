"""Shared ASGI composition builder for Network Check source entrypoints."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from network_check.web.api import router as api_router
from network_check.web.legacy import router as legacy_router
from network_check.web.metrics import router as metrics_router
from network_check.web.public import router as public_router


def create_network_check_app() -> FastAPI:
    """Build the shared Network Check application composition."""

    application = FastAPI(
        title="Network Check",
        description="Simple IPv4/IPv6 and DNS A/AAAA check site.",
    )
    application.mount("/static", StaticFiles(directory="static"), name="static")
    application.include_router(legacy_router)
    application.include_router(public_router)
    application.include_router(api_router)
    application.include_router(metrics_router)
    return application
