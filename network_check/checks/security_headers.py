from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request

from typing import Any

SECURITY_HEADER_NAMES = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]

LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
}

DEFAULT_HTTP_PORTS = {
    "http": 80,
    "https": 443,
}

def is_disallowed_target_ip(ip_text: str) -> bool:
    try:
        parsed = ipaddress.ip_address(ip_text)
    except ValueError:
        return True

    return (
        not parsed.is_global
        or parsed.is_private
        or parsed.is_loopback
        or parsed.is_link_local
        or parsed.is_multicast
        or parsed.is_unspecified
        or parsed.is_reserved
    )

def normalize_security_header_url(url_input: str) -> dict[str, Any]:
    raw_input = url_input.strip()

    if not raw_input:
        return {
            "ok": False,
            "url": raw_input,
            "error": "URL is required. / URLを入力してください。",
        }

    parsed = urllib.parse.urlparse(raw_input)

    if parsed.scheme.lower() not in {"http", "https"}:
        return {
            "ok": False,
            "url": raw_input,
            "error": "Only http:// and https:// URLs are supported. / http:// または https:// のURLのみ対応します。",
        }

    if parsed.username or parsed.password:
        return {
            "ok": False,
            "url": raw_input,
            "error": "URLs with embedded credentials are not allowed. / 認証情報を含むURLは許可しません。",
        }

    hostname = parsed.hostname
    if not hostname:
        return {
            "ok": False,
            "url": raw_input,
            "error": "URL host is missing. / URLのホスト名がありません。",
        }

    hostname = hostname.strip().rstrip(".")
    if hostname.lower() in LOCAL_HOSTNAMES:
        return {
            "ok": False,
            "url": raw_input,
            "error": "Localhost targets are not allowed. / localhost 宛先は許可しません。",
        }

    try:
        ip_literal = ipaddress.ip_address(hostname)
        normalized_host = str(ip_literal)
        host_for_url = f"[{normalized_host}]" if ip_literal.version == 6 else normalized_host
    except ValueError:
        try:
            normalized_host = hostname.encode("idna").decode("ascii").lower()
        except UnicodeError:
            return {
                "ok": False,
                "url": raw_input,
                "error": "Invalid hostname. / ホスト名の形式が正しくありません。",
            }
        host_for_url = normalized_host

    scheme = parsed.scheme.lower()
    expected_port = DEFAULT_HTTP_PORTS[scheme]

    try:
        requested_port = parsed.port
    except ValueError:
        return {
            "ok": False,
            "url": raw_input,
            "error": "Invalid port number. / ポート番号の形式が正しくありません。",
        }

    if requested_port is not None and requested_port != expected_port:
        return {
            "ok": False,
            "url": raw_input,
            "error": "Only default HTTP/HTTPS ports are allowed. / HTTP/HTTPSの標準ポートのみ許可します。",
        }

    port = requested_port or expected_port
    netloc = host_for_url if requested_port is None else f"{host_for_url}:{requested_port}"
    path = parsed.path or "/"

    normalized_url = urllib.parse.urlunparse(
        (scheme, netloc, path, parsed.params, parsed.query, "")
    )

    return {
        "ok": True,
        "url": normalized_url,
        "host": normalized_host,
        "port": port,
    }

def resolve_public_target(host: str, port: int) -> dict[str, Any]:
    try:
        addrinfo = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {
            "ok": False,
            "error": f"Name resolution failed. / 名前解決に失敗しました: {exc}",
        }

    resolved_ips = sorted({item[4][0] for item in addrinfo})

    if not resolved_ips:
        return {
            "ok": False,
            "error": "No target address was resolved. / 宛先IPアドレスが解決できませんでした。",
        }

    blocked_ips = [ip for ip in resolved_ips if is_disallowed_target_ip(ip)]
    if blocked_ips:
        return {
            "ok": False,
            "resolved_ips": resolved_ips,
            "blocked_ips": blocked_ips,
            "error": "Target resolves to a non-public address. / 対象ホストが公開用ではないIPアドレスへ解決されました。",
        }

    return {
        "ok": True,
        "resolved_ips": resolved_ips,
    }

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def perform_security_header_request(url: str, method: str) -> dict[str, Any]:
    request_headers = {
        "User-Agent": "NetworkCheck/1.0",
        "Accept": "*/*",
        "Connection": "close",
    }

    if method == "GET":
        request_headers["Range"] = "bytes=0-0"

    request = urllib.request.Request(
        url,
        method=method,
        headers=request_headers,
    )

    opener = urllib.request.build_opener(NoRedirectHandler)

    try:
        with opener.open(request, timeout=8) as response:
            return {
                "ok": True,
                "status_code": response.status,
                "reason": response.reason,
                "headers": response.headers,
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": True,
            "status_code": exc.code,
            "reason": exc.reason,
            "headers": exc.headers,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }

def check_security_headers(url_input: str) -> dict[str, Any]:
    normalized = normalize_security_header_url(url_input)

    if not normalized["ok"]:
        return normalized

    resolved = resolve_public_target(normalized["host"], normalized["port"])
    if not resolved["ok"]:
        return {
            "ok": False,
            "url": normalized["url"],
            "host": normalized["host"],
            "error": resolved["error"],
            "resolved_ips": resolved.get("resolved_ips", []),
            "blocked_ips": resolved.get("blocked_ips", []),
        }

    request_result = perform_security_header_request(normalized["url"], "HEAD")
    method_used = "HEAD"

    if request_result["ok"] and request_result.get("status_code") in {405, 501}:
        request_result = perform_security_header_request(normalized["url"], "GET")
        method_used = "GET"
    elif not request_result["ok"]:
        request_result = perform_security_header_request(normalized["url"], "GET")
        method_used = "GET"

    if not request_result["ok"]:
        return {
            "ok": False,
            "url": normalized["url"],
            "host": normalized["host"],
            "resolved_ips": resolved["resolved_ips"],
            "error": f"HTTP request failed. / HTTPリクエストに失敗しました: {request_result['error']}",
        }

    response_headers = request_result["headers"]
    header_items = []

    for header_name in SECURITY_HEADER_NAMES:
        value = response_headers.get(header_name)
        header_items.append({
            "name": header_name,
            "value": value,
            "present": bool(value),
        })

    present_count = sum(1 for item in header_items if item["present"])

    level = "good" if present_count else "warn"

    return {
        "ok": True,
        "url": normalized["url"],
        "host": normalized["host"],
        "resolved_ips": resolved["resolved_ips"],
        "method": method_used,
        "status_code": request_result["status_code"],
        "reason": request_result.get("reason", ""),
        "header_items": header_items,
        "present_count": present_count,
        "status": "Security headers checked. / セキュリティヘッダーを確認しました。",
        "level": level,
    }
