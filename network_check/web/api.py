from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from network_check.application.multi_check import run_multi_check
from network_check.usage_metrics import record_usage_event


router = APIRouter()


@router.post("/api/multi-check/run")
async def multi_check_run(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        payload = None

    return run_multi_check(
        payload,
        record_usage=record_usage_event,
    )

@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
