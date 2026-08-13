from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from network_check.usage_metrics import get_usage_dashboard, usage_metrics_status
from network_check.web.context import template_context, templates


router = APIRouter()


@router.get("/usage-metrics", response_class=HTMLResponse)
async def usage_metrics(request: Request) -> HTMLResponse:
    metrics_error = None
    usage_dashboard: dict[str, Any] = {}
    try:
        usage_dashboard = get_usage_dashboard()
    except Exception:
        metrics_error = "Usage metrics are temporarily unavailable. / 利用状況の集計を一時的に表示できません。"

    # db_path is runtime/internal detail and is intentionally excluded from
    # the template context, not just left unrendered by the template.
    metrics_status = {"db_exists": usage_metrics_status()["db_exists"]}

    return templates.TemplateResponse(
        "usage_metrics.html",
        template_context(
            request,
            "usage_metrics",
            usage_dashboard=usage_dashboard,
            metrics_status=metrics_status,
            metrics_error=metrics_error,
        ),
    )
