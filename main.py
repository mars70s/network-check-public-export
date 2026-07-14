from __future__ import annotations

import os
import ipaddress

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from network_check.checks.caa import check_caa
from network_check.checks.dns import check_domain
from network_check.checks.dns_timing import check_dns_timing
from network_check.checks.http2 import check_http2
from network_check.checks.ip_preference import check_ip_preference
from network_check.checks.mail import (
    check_dmarc_records,
    check_mx_records,
    check_spf_records,
)
from network_check.checks.ptr import check_ptr
from network_check.checks.security_headers import check_security_headers
from network_check.checks.tls import check_tls
from network_check.public_explanations import (
    get_public_explanation,
    guide_explanation_items,
)
from network_check.usage_metrics import (
    get_usage_dashboard,
    record_usage_event,
    usage_metrics_status,
)

app = FastAPI(title="Network Check", description="Simple IPv4/IPv6 and DNS A/AAAA check site.")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()

SITE_NAME = os.getenv("SITE_NAME", "Network Check")
PUBLIC_BASE_PATH = os.getenv("PUBLIC_BASE_PATH", "")
CONTACT_NAME = os.getenv("CONTACT_NAME", "Network Check Project")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "contact@example.com")


CHECK_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "domain",
        "label": "Domain",
        "category": "dns",
        "category_label": "DNS",
        "description": "A / AAAA / CNAME / NS / SOA",
        "default_selected": True,
        "multi_check": True,
        "ui_order": 10,
        "function": check_domain,
    },
    {
        "id": "ip_preference",
        "label": "IP Preference",
        "category": "ip",
        "category_label": "IP",
        "description": "IPv4 / IPv6 availability",
        "default_selected": True,
        "multi_check": True,
        "ui_order": 90,
        "function": check_ip_preference,
    },
    {
        "id": "dns_timing",
        "label": "DNS Timing",
        "category": "dns",
        "category_label": "DNS",
        "description": "A / AAAA response timing",
        "default_selected": False,
        "multi_check": True,
        "ui_order": 20,
        "function": check_dns_timing,
    },
    {
        "id": "tls",
        "label": "TLS",
        "category": "web",
        "category_label": "WEB",
        "description": "Certificate and cipher",
        "default_selected": False,
        "multi_check": True,
        "ui_order": 70,
        "function": check_tls,
    },
    {
        "id": "http2",
        "label": "HTTP/2",
        "category": "web",
        "category_label": "WEB",
        "description": "HTTPS negotiation",
        "default_selected": False,
        "multi_check": True,
        "ui_order": 80,
        "function": check_http2,
    },
    {
        "id": "mx",
        "label": "MX",
        "category": "mail",
        "category_label": "MAIL",
        "description": "Mail exchanger records",
        "default_selected": True,
        "multi_check": True,
        "ui_order": 40,
        "function": check_mx_records,
    },
    {
        "id": "spf",
        "label": "SPF",
        "category": "mail",
        "category_label": "MAIL",
        "description": "Sender policy TXT",
        "default_selected": True,
        "multi_check": True,
        "ui_order": 50,
        "function": check_spf_records,
    },
    {
        "id": "dmarc",
        "label": "DMARC",
        "category": "mail",
        "category_label": "MAIL",
        "description": "Mail authentication policy",
        "default_selected": True,
        "multi_check": True,
        "ui_order": 60,
        "function": check_dmarc_records,
    },
    {
        "id": "caa",
        "label": "CAA",
        "category": "dns",
        "category_label": "DNS",
        "description": "Certificate authority policy",
        "default_selected": False,
        "multi_check": True,
        "ui_order": 30,
        "function": check_caa,
    },
]

MULTI_CHECK_DEFINITIONS = [
    definition for definition in CHECK_DEFINITIONS if definition["multi_check"]
]

MULTI_CHECK_FUNCTIONS = {
    str(definition["id"]): definition["function"]
    for definition in MULTI_CHECK_DEFINITIONS
}

MULTI_CHECK_ORDER = [
    str(definition["id"]) for definition in MULTI_CHECK_DEFINITIONS
]


def multi_check_ui_options() -> list[dict[str, Any]]:
    public_fields = (
        "id",
        "label",
        "category",
        "category_label",
        "description",
        "default_selected",
        "ui_order",
    )
    return [
        {field: definition[field] for field in public_fields}
        for definition in sorted(
            MULTI_CHECK_DEFINITIONS,
            key=lambda definition: int(definition["ui_order"]),
        )
    ]


def template_context(request: Request, page: str, **extra: Any) -> dict[str, Any]:
    context: dict[str, Any] = {
        "request": request,
        "page": page,
        "site_name": SITE_NAME,
        "contact_name": CONTACT_NAME,
        "contact_email": CONTACT_EMAIL,
        "base_path": PUBLIC_BASE_PATH,
    }
    context.update(extra)
    return context


def public_template_context(request: Request, page: str, **extra: Any) -> dict[str, Any]:
    context = template_context(request, page, public_path="/network-check")
    context.update(extra)
    return context


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    return request.client.host if request.client else "unknown"


def ip_version(ip: str) -> str:
    try:
        parsed = ipaddress.ip_address(ip)
        return "IPv4" if parsed.version == 4 else "IPv6"
    except ValueError:
        return "Unknown / 不明"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    client_ip = get_client_ip(request)
    data = {
        "ip": client_ip,
        "ip_version": ip_version(client_ip),
        "user_agent": request.headers.get("user-agent", "Unknown / 不明"),
        "accept_language": request.headers.get("accept-language", "Unknown / 不明"),
    }
    return templates.TemplateResponse("index.html", template_context(request, "home", data=data))


@app.get("/checks", response_class=HTMLResponse)
async def checks(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("checks.html", template_context(request, "checks"))


@app.get("/multi-check", response_class=HTMLResponse)
async def multi_check_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "multi_check.html",
        template_context(
            request,
            "multi_check",
            multi_check_options=multi_check_ui_options(),
        ),
    )


@app.get("/network-check/", response_class=HTMLResponse)
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



@app.get("/network-check/guide/", response_class=HTMLResponse)
async def public_explanation_guide(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "public_explanation_guide.html",
        public_template_context(
            request,
            "public_explanation_guide",
            guide_items=guide_explanation_items(),
        ),
    )


@app.get("/network-check/{slug}/", response_class=HTMLResponse)
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


@app.post("/api/multi-check/run")
async def multi_check_run(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        return {
            "ok": False,
            "error": "Invalid request.",
            "results": {},
            "errors": {},
        }

    domain = payload.get("domain") if isinstance(payload, dict) else None
    checks = payload.get("checks") if isinstance(payload, dict) else None

    if not isinstance(domain, str) or not domain.strip() or not isinstance(checks, list):
        return {
            "ok": False,
            "error": "Invalid request.",
            "results": {},
            "errors": {},
        }

    selected_checks = []
    invalid_checks = []
    for check_id in checks:
        if not isinstance(check_id, str) or check_id not in MULTI_CHECK_FUNCTIONS:
            invalid_checks.append(check_id)
            continue
        if check_id not in selected_checks:
            selected_checks.append(check_id)

    if invalid_checks or not selected_checks:
        return {
            "ok": False,
            "domain": domain.strip(),
            "error": "Invalid request.",
            "results": {},
            "errors": {
                "checks": "Unknown or unsupported check id.",
            },
        }

    record_usage_event("multi_check_run", "all")
    for check_id in selected_checks:
        record_usage_event("multi_check_selected", check_id)

    results: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    for check_id in MULTI_CHECK_ORDER:
        if check_id not in selected_checks:
            continue
        check_function = MULTI_CHECK_FUNCTIONS[check_id]
        try:
            result = check_function(domain)
            results[check_id] = {
                "ok": bool(result.get("ok")),
                "result": result,
            }
        except Exception as exc:
            error_result = {
                "ok": False,
                "domain": domain.strip(),
                "error": str(exc),
            }
            results[check_id] = {
                "ok": False,
                "result": error_result,
            }
            errors[check_id] = str(exc)

    return {
        "ok": True,
        "domain": domain.strip(),
        "results": results,
        "errors": errors,
    }


@app.get("/domain", response_class=HTMLResponse)
async def domain_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=None, domain_input=""))


@app.post("/domain", response_class=HTMLResponse)
async def domain_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=check_domain(domain), domain_input=domain))


@app.get("/caa", response_class=HTMLResponse)
async def caa_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("caa.html", template_context(request, "caa", result=None, domain_input=""))


@app.post("/caa", response_class=HTMLResponse)
async def caa_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("caa.html", template_context(request, "caa", result=check_caa(domain), domain_input=domain))


@app.get("/security-headers", response_class=HTMLResponse)
async def security_headers_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "security_headers.html",
        template_context(request, "security_headers", result=None, url_input=""),
    )


@app.post("/security-headers", response_class=HTMLResponse)
async def security_headers_post(request: Request, url: str = Form(...)) -> HTMLResponse:
    result = check_security_headers(url)
    return templates.TemplateResponse(
        "security_headers.html",
        template_context(request, "security_headers", result=result, url_input=url),
    )


@app.get("/ptr", response_class=HTMLResponse)
async def ptr_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("ptr.html", template_context(request, "ptr", result=None, ip_input=""))


@app.post("/ptr", response_class=HTMLResponse)
async def ptr_post(request: Request, ip_input: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("ptr.html", template_context(request, "ptr", result=check_ptr(ip_input), ip_input=ip_input))


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("privacy.html", template_context(request, "privacy"))


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("terms.html", template_context(request, "terms"))


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("contact.html", template_context(request, "contact"))


@app.get("/tls", response_class=HTMLResponse)
async def tls_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "tls.html",
        template_context(request, "tls", result=None, domain_input=""),
    )


@app.post("/tls", response_class=HTMLResponse)
async def tls_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_tls(domain)
    return templates.TemplateResponse(
        "tls.html",
        template_context(request, "tls", result=result, domain_input=domain),
    )


@app.get("/http2", response_class=HTMLResponse)
async def http2_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "http2.html",
        template_context(request, "http2", result=None, domain_input=""),
    )


@app.post("/http2", response_class=HTMLResponse)
async def http2_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_http2(domain)
    return templates.TemplateResponse(
        "http2.html",
        template_context(request, "http2", result=result, domain_input=domain),
    )


@app.get("/dns-timing", response_class=HTMLResponse)
async def dns_timing_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "dns_timing.html",
        template_context(request, "dns_timing", result=None, domain_input=""),
    )


@app.post("/dns-timing", response_class=HTMLResponse)
async def dns_timing_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_dns_timing(domain)
    return templates.TemplateResponse(
        "dns_timing.html",
        template_context(request, "dns_timing", result=result, domain_input=domain),
    )


@app.get("/ip-preference", response_class=HTMLResponse)
async def ip_preference_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ip_preference.html",
        template_context(request, "ip_preference", result=None, domain_input=""),
    )


@app.post("/ip-preference", response_class=HTMLResponse)
async def ip_preference_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_ip_preference(domain)
    return templates.TemplateResponse(
        "ip_preference.html",
        template_context(request, "ip_preference", result=result, domain_input=domain),
    )


@app.get("/mx", response_class=HTMLResponse)
async def mx_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "mx.html",
        template_context(request, "mx", result=None, domain_input=""),
    )


@app.post("/mx", response_class=HTMLResponse)
async def mx_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_mx_records(domain)
    return templates.TemplateResponse(
        "mx.html",
        template_context(request, "mx", result=result, domain_input=domain),
    )


@app.get("/spf", response_class=HTMLResponse)
async def spf_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "spf.html",
        template_context(request, "spf", result=None, domain_input=""),
    )


@app.post("/spf", response_class=HTMLResponse)
async def spf_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_spf_records(domain)
    return templates.TemplateResponse(
        "spf.html",
        template_context(request, "spf", result=result, domain_input=domain),
    )


@app.get("/dmarc", response_class=HTMLResponse)
async def dmarc_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "dmarc.html",
        template_context(request, "dmarc", result=None, domain_input=""),
    )


@app.post("/dmarc", response_class=HTMLResponse)
async def dmarc_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_dmarc_records(domain)
    return templates.TemplateResponse(
        "dmarc.html",
        template_context(request, "dmarc", result=result, domain_input=domain),
    )


@app.get("/usage-metrics", response_class=HTMLResponse)
async def usage_metrics(request: Request) -> HTMLResponse:
    metrics_error = None
    usage_dashboard: dict[str, Any] = {}
    try:
        usage_dashboard = get_usage_dashboard()
    except Exception as exc:
        metrics_error = str(exc)
    return templates.TemplateResponse(
        "usage_metrics.html",
        template_context(
            request,
            "usage_metrics",
            usage_dashboard=usage_dashboard,
            metrics_status=usage_metrics_status(),
            metrics_error=metrics_error,
        ),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
