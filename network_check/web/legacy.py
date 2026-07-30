from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

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
from network_check.web.context import (
    get_client_ip,
    ip_version,
    template_context,
    templates,
)
from network_check.web.multi_check_catalog import multi_check_ui_options


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    client_ip = get_client_ip(request)
    data = {
        "ip": client_ip,
        "ip_version": ip_version(client_ip),
        "user_agent": request.headers.get("user-agent", "Unknown / 不明"),
        "accept_language": request.headers.get("accept-language", "Unknown / 不明"),
    }
    return templates.TemplateResponse("index.html", template_context(request, "home", data=data))

@router.get("/checks", response_class=HTMLResponse)
async def checks(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("checks.html", template_context(request, "checks"))

@router.get("/multi-check", response_class=HTMLResponse)
async def multi_check_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "multi_check.html",
        template_context(
            request,
            "multi_check",
            multi_check_options=multi_check_ui_options(),
        ),
    )

@router.get("/domain", response_class=HTMLResponse)
async def domain_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=None, domain_input=""))

@router.post("/domain", response_class=HTMLResponse)
async def domain_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=check_domain(domain), domain_input=domain))

@router.get("/caa", response_class=HTMLResponse)
async def caa_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("caa.html", template_context(request, "caa", result=None, domain_input=""))

@router.post("/caa", response_class=HTMLResponse)
async def caa_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("caa.html", template_context(request, "caa", result=check_caa(domain), domain_input=domain))

@router.get("/security-headers", response_class=HTMLResponse)
async def security_headers_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "security_headers.html",
        template_context(request, "security_headers", result=None, url_input=""),
    )

@router.post("/security-headers", response_class=HTMLResponse)
async def security_headers_post(request: Request, url: str = Form(...)) -> HTMLResponse:
    result = check_security_headers(url)
    return templates.TemplateResponse(
        "security_headers.html",
        template_context(request, "security_headers", result=result, url_input=url),
    )

@router.get("/ptr", response_class=HTMLResponse)
async def ptr_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("ptr.html", template_context(request, "ptr", result=None, ip_input=""))

@router.post("/ptr", response_class=HTMLResponse)
async def ptr_post(request: Request, ip_input: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("ptr.html", template_context(request, "ptr", result=check_ptr(ip_input), ip_input=ip_input))

@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("privacy.html", template_context(request, "privacy"))

@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("terms.html", template_context(request, "terms"))

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("contact.html", template_context(request, "contact"))

@router.get("/tls", response_class=HTMLResponse)
async def tls_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "tls.html",
        template_context(request, "tls", result=None, domain_input=""),
    )

@router.post("/tls", response_class=HTMLResponse)
async def tls_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_tls(domain)
    return templates.TemplateResponse(
        "tls.html",
        template_context(request, "tls", result=result, domain_input=domain),
    )

@router.get("/http2", response_class=HTMLResponse)
async def http2_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "http2.html",
        template_context(request, "http2", result=None, domain_input=""),
    )

@router.post("/http2", response_class=HTMLResponse)
async def http2_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_http2(domain)
    return templates.TemplateResponse(
        "http2.html",
        template_context(request, "http2", result=result, domain_input=domain),
    )

@router.get("/dns-timing", response_class=HTMLResponse)
async def dns_timing_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "dns_timing.html",
        template_context(request, "dns_timing", result=None, domain_input=""),
    )

@router.post("/dns-timing", response_class=HTMLResponse)
async def dns_timing_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_dns_timing(domain)
    return templates.TemplateResponse(
        "dns_timing.html",
        template_context(request, "dns_timing", result=result, domain_input=domain),
    )

@router.get("/ip-preference", response_class=HTMLResponse)
async def ip_preference_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "ip_preference.html",
        template_context(request, "ip_preference", result=None, domain_input=""),
    )

@router.post("/ip-preference", response_class=HTMLResponse)
async def ip_preference_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_ip_preference(domain)
    return templates.TemplateResponse(
        "ip_preference.html",
        template_context(request, "ip_preference", result=result, domain_input=domain),
    )

@router.get("/mx", response_class=HTMLResponse)
async def mx_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "mx.html",
        template_context(request, "mx", result=None, domain_input=""),
    )

@router.post("/mx", response_class=HTMLResponse)
async def mx_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_mx_records(domain)
    return templates.TemplateResponse(
        "mx.html",
        template_context(request, "mx", result=result, domain_input=domain),
    )

@router.get("/spf", response_class=HTMLResponse)
async def spf_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "spf.html",
        template_context(request, "spf", result=None, domain_input=""),
    )

@router.post("/spf", response_class=HTMLResponse)
async def spf_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_spf_records(domain)
    return templates.TemplateResponse(
        "spf.html",
        template_context(request, "spf", result=result, domain_input=domain),
    )

@router.get("/dmarc", response_class=HTMLResponse)
async def dmarc_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "dmarc.html",
        template_context(request, "dmarc", result=None, domain_input=""),
    )

@router.post("/dmarc", response_class=HTMLResponse)
async def dmarc_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    result = check_dmarc_records(domain)
    return templates.TemplateResponse(
        "dmarc.html",
        template_context(request, "dmarc", result=result, domain_input=domain),
    )
