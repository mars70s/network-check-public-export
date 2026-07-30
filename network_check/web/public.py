from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from network_check.public_explanations import (
    get_public_explanation,
    guide_explanation_items,
)
from network_check.usage_metrics import record_usage_event
from network_check.web.context import public_template_context, templates
from network_check.web.multi_check_catalog import multi_check_ui_options


router = APIRouter()


@router.get("/network-check/", response_class=HTMLResponse)
async def public_network_check(request: Request) -> HTMLResponse:
    record_usage_event("public_page_view", "network_check_home")
    return templates.TemplateResponse(
        "public_network_check.html",
        public_template_context(
            request,
            "public_network_check",
            multi_check_options=multi_check_ui_options(),
        ),
    )

@router.get("/network-check/guide/", response_class=HTMLResponse)
async def public_explanation_guide(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "public_explanation_guide.html",
        public_template_context(
            request,
            "public_explanation_guide",
            guide_items=guide_explanation_items(),
        ),
    )

@router.get("/network-check/{slug}/", response_class=HTMLResponse)
async def public_explanation(request: Request, slug: str) -> HTMLResponse:
    explanation = get_public_explanation(slug)
    if explanation is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "public_explanation.html",
        public_template_context(
            request,
            "public_explanation",
            explanation=explanation,
        ),
    )
