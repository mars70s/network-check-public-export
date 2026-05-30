from __future__ import annotations

import os
import ipaddress
import re
import socket
import ssl
import time
import subprocess

from typing import Any

import dns.resolver
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Network Check", description="Simple IPv4/IPv6 and DNS A/AAAA check site.")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()

SITE_NAME = os.getenv("SITE_NAME", "Network Check")
PUBLIC_BASE_PATH = os.getenv("PUBLIC_BASE_PATH", "")
CONTACT_NAME = os.getenv("CONTACT_NAME", "Network Check Project")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "contact@example.com")

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}\.?$")

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

def normalize_domain(domain: str) -> str:
    domain = domain.strip().removeprefix("http://").removeprefix("https://")
    domain = domain.split("/")[0].split(":")[0]
    return domain.lower().rstrip(".")

def resolve_records(domain: str, record_type: str) -> list[str]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0
    resolver.timeout = 2.0
    try:
        answers = resolver.resolve(domain, record_type)
        return sorted({answer.to_text() for answer in answers})
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        return []
    except Exception:
        return []

def check_domain(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)
    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {"ok": False, "domain": normalized, "error": "Invalid domain format. / ドメイン名の形式が正しくありません。"}
    a_records = resolve_records(normalized, "A")
    aaaa_records = resolve_records(normalized, "AAAA")
    if a_records and aaaa_records:
        status = "Dual-stack: IPv4 and IPv6 / IPv4・IPv6 両対応"
        message = "This domain has both A and AAAA records. / このドメインはIPv4とIPv6の両方のDNSレコードを持っています。"
        level = "good"
    elif a_records and not aaaa_records:
        status = "IPv4 only / IPv4のみ対応"
        message = "A records were found, but no AAAA records were found. / Aレコードはありますが、AAAAレコードは見つかりませんでした。"
        level = "warn"
    elif not a_records and aaaa_records:
        status = "IPv6 only / IPv6のみ対応"
        message = "AAAA records were found, but no A records were found. / AAAAレコードはありますが、Aレコードは見つかりませんでした。"
        level = "good"
    else:
        status = "No web DNS records found / Web用DNSレコード未検出"
        message = "No A or AAAA records were found. The domain may be mistyped or use a special configuration. / A・AAAAレコードが見つかりませんでした。入力ミスや特殊な構成の可能性があります。"
        level = "bad"
    return {"ok": True, "domain": normalized, "a_records": a_records, "aaaa_records": aaaa_records, "status": status, "message": message, "level": level}


def check_tls(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    try:
        context = ssl.create_default_context()
        with socket.create_connection((normalized, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=normalized) as tls_sock:
                tls_version = tls_sock.version()
                cipher = tls_sock.cipher()

        if tls_version == "TLSv1.3":
            level = "good"
            status = "Modern TLS / 新しいTLS"
        elif tls_version == "TLSv1.2":
            level = "warn"
            status = "TLS 1.2 / TLS 1.2"
        else:
            level = "bad"
            status = "Legacy TLS / 古いTLS"

        return {
            "ok": True,
            "domain": normalized,
            "tls_version": tls_version,
            "cipher": cipher[0] if cipher else "Unknown",
            "cipher_protocol": cipher[1] if cipher else "Unknown",
            "cipher_bits": cipher[2] if cipher else "Unknown",
            "status": status,
            "level": level,
        }

    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "error": f"TLS connection failed. / TLS接続に失敗しました: {exc}",
        }

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

@app.get("/domain", response_class=HTMLResponse)
async def domain_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=None, domain_input=""))

@app.post("/domain", response_class=HTMLResponse)
async def domain_post(request: Request, domain: str = Form(...)) -> HTMLResponse:
    return templates.TemplateResponse("domain.html", template_context(request, "domain", result=check_domain(domain), domain_input=domain))

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("privacy.html", template_context(request, "privacy"))

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("terms.html", template_context(request, "terms"))

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("contact.html", template_context(request, "contact"))



def check_http2(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    try:
        version_result = subprocess.run(
            ["curl", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if "HTTP2" not in version_result.stdout:
            return {
                "ok": True,
                "domain": normalized,
                "available": False,
                "status": "HTTP/2 check unavailable on this runtime. / この実行環境ではHTTP/2確認を利用できません。",
                "level": "warn",
            }

        target_url = f"https://{normalized}/"

        result = subprocess.run(
            ["curl", "-I", "--http2", "-L", "-s", "-o", "NUL", "-w", "%{http_version} %{http_code} %{url_effective}", target_url],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout.strip()
        parts = output.split(" ", 2)

        http_version = parts[0] if len(parts) > 0 else "unknown"
        status_code = parts[1] if len(parts) > 1 else "unknown"
        final_url = parts[2] if len(parts) > 2 else target_url

        if http_version == "2":
            level = "good"
            status = "HTTP/2 negotiated. / HTTP/2で接続されました。"
        else:
            level = "warn"
            status = "HTTP/2 was not negotiated. / HTTP/2では接続されませんでした。"

        return {
            "ok": True,
            "available": True,
            "domain": normalized,
            "http_version": http_version,
            "status_code": status_code,
            "final_url": final_url,
            "status": status,
            "level": level,
        }

    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "error": f"HTTP/2 check failed. / HTTP/2確認に失敗しました: {exc}",
        }

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



def timed_resolve_records(domain: str, record_type: str) -> dict[str, Any]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0
    resolver.timeout = 2.0

    started = time.perf_counter()
    try:
        answers = resolver.resolve(domain, record_type)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": True,
            "record_type": record_type,
            "records": sorted({answer.to_text() for answer in answers}),
            "elapsed_ms": elapsed_ms,
            "error": None,
        }
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ) as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "record_type": record_type,
            "records": [],
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
        }
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "record_type": record_type,
            "records": [],
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
        }


def check_dns_timing(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    a_result = timed_resolve_records(normalized, "A")
    aaaa_result = timed_resolve_records(normalized, "AAAA")

    has_any_record = bool(a_result["records"] or aaaa_result["records"])

    if has_any_record:
        level = "good"
        status = "DNS response timing completed. / DNS応答時間を確認しました。"
    else:
        level = "warn"
        status = "No A or AAAA records found. / AまたはAAAAレコードが見つかりませんでした。"

    return {
        "ok": True,
        "domain": normalized,
        "a_result": a_result,
        "aaaa_result": aaaa_result,
        "status": status,
        "level": level,
    }

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



def check_ip_preference(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    a_records = resolve_records(normalized, "A")
    aaaa_records = resolve_records(normalized, "AAAA")

    has_ipv4 = bool(a_records)
    has_ipv6 = bool(aaaa_records)

    if has_ipv4 and has_ipv6:
        level = "good"
        status = "Dual-stack / IPv4・IPv6 両対応"
        summary = "This domain publishes both A and AAAA records. / このドメインはAレコードとAAAAレコードの両方を公開しています。"
        preference = "IPv4 and IPv6 available / IPv4・IPv6利用可能"
    elif has_ipv4 and not has_ipv6:
        level = "warn"
        status = "IPv4 only / IPv4のみ"
        summary = "This domain publishes A records but no AAAA records. / このドメインはAレコードを公開していますが、AAAAレコードは公開していません。"
        preference = "IPv4 preferred by availability / 利用可能性ではIPv4優先"
    elif not has_ipv4 and has_ipv6:
        level = "good"
        status = "IPv6 only / IPv6のみ"
        summary = "This domain publishes AAAA records but no A records. / このドメインはAAAAレコードを公開していますが、Aレコードは公開していません。"
        preference = "IPv6 preferred by availability / 利用可能性ではIPv6優先"
    else:
        level = "bad"
        status = "No A or AAAA records / A・AAAAレコードなし"
        summary = "No A or AAAA records were found. / AレコードまたはAAAAレコードが見つかりませんでした。"
        preference = "No IP version preference can be determined. / IPバージョン優先状況は判定できません。"

    return {
        "ok": True,
        "domain": normalized,
        "a_records": a_records,
        "aaaa_records": aaaa_records,
        "has_ipv4": has_ipv4,
        "has_ipv6": has_ipv6,
        "status": status,
        "summary": summary,
        "preference": preference,
        "level": level,
    }

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


def check_mx_records(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    try:
        answers = dns.resolver.resolve(normalized, "MX")
        records = sorted(
            [
                {
                    "preference": answer.preference,
                    "exchange": str(answer.exchange).rstrip("."),
                }
                for answer in answers
            ],
            key=lambda item: (item["preference"], item["exchange"]),
        )

        if records:
            return {
                "ok": True,
                "domain": normalized,
                "records": records,
                "status": "MX records found. / MXレコードが見つかりました。",
                "level": "good",
            }

        return {
            "ok": True,
            "domain": normalized,
            "records": [],
            "status": "No MX records found. / MXレコードが見つかりませんでした。",
            "level": "warn",
        }

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ) as exc:
        return {
            "ok": True,
            "domain": normalized,
            "records": [],
            "status": "No MX records found. / MXレコードが見つかりませんでした。",
            "level": "warn",
            "detail": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "error": f"MX record check failed. / MXレコード確認に失敗しました: {exc}",
        }


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


def check_spf_records(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    try:
        answers = dns.resolver.resolve(normalized, "TXT")
        txt_records = [answer.to_text().strip('"') for answer in answers]
        spf_records = [record for record in txt_records if record.lower().startswith("v=spf1")]

        if spf_records:
            return {
                "ok": True,
                "domain": normalized,
                "records": spf_records,
                "status": "SPF record found. / SPFレコードが見つかりました。",
                "level": "good",
            }

        return {
            "ok": True,
            "domain": normalized,
            "records": [],
            "status": "No SPF record found. / SPFレコードが見つかりませんでした。",
            "level": "warn",
        }

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ) as exc:
        return {
            "ok": True,
            "domain": normalized,
            "records": [],
            "status": "No SPF record found. / SPFレコードが見つかりませんでした。",
            "level": "warn",
            "detail": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "error": f"SPF record check failed. / SPFレコード確認に失敗しました: {exc}",
        }


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


def check_dmarc_records(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    dmarc_domain = f"_dmarc.{normalized}"

    try:
        answers = dns.resolver.resolve(dmarc_domain, "TXT")
        txt_records = [answer.to_text().strip('"') for answer in answers]
        dmarc_records = [record for record in txt_records if record.upper().startswith("V=DMARC1")]

        if dmarc_records:
            return {
                "ok": True,
                "domain": normalized,
                "query_domain": dmarc_domain,
                "records": dmarc_records,
                "status": "DMARC record found. / DMARCレコードが見つかりました。",
                "level": "good",
            }

        return {
            "ok": True,
            "domain": normalized,
            "query_domain": dmarc_domain,
            "records": [],
            "status": "No DMARC record found. / DMARCレコードが見つかりませんでした。",
            "level": "warn",
        }

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ) as exc:
        return {
            "ok": True,
            "domain": normalized,
            "query_domain": dmarc_domain,
            "records": [],
            "status": "No DMARC record found. / DMARCレコードが見つかりませんでした。",
            "level": "warn",
            "detail": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "query_domain": dmarc_domain,
            "error": f"DMARC record check failed. / DMARCレコード確認に失敗しました: {exc}",
        }


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

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}









