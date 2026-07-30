from __future__ import annotations

import ipaddress
import os
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

SITE_NAME = os.getenv("SITE_NAME", "Network Check")
PUBLIC_BASE_PATH = os.getenv("PUBLIC_BASE_PATH", "")
CONTACT_NAME = os.getenv("CONTACT_NAME", "Network Check Project")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "contact@example.com")


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
