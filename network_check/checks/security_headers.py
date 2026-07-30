from __future__ import annotations

import http.client
import ipaddress
import ssl
import urllib.parse

from typing import Any

from .destination_guard import (
    ConnectCandidate,
    assert_public_connect_target,
    is_disallowed_target_ip,
    open_validated_tcp_socket,
)

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
    result = assert_public_connect_target(host, port)
    if not result["ok"] and result.get("is_ip_literal") and result.get("blocked_ips"):
        result = dict(result)
        result["error"] = "Target resolves to a non-public address. / 対象ホストが公開用ではないIPアドレスへ解決されました。"
    return result


def _request_target(parsed: urllib.parse.ParseResult) -> str:
    target = parsed.path or "/"
    if parsed.params:
        target += f";{parsed.params}"
    if parsed.query:
        target += f"?{parsed.query}"
    return target


def _open_http_connection(
    parsed: urllib.parse.ParseResult,
    candidate: ConnectCandidate,
    timeout: float,
) -> http.client.HTTPConnection:
    host = parsed.hostname
    if host is None:
        raise ValueError("URL host is missing.")

    port = parsed.port or DEFAULT_HTTP_PORTS[parsed.scheme]
    connection: http.client.HTTPConnection

    if parsed.scheme == "https":
        context = ssl.create_default_context()
        connection = http.client.HTTPSConnection(host, port, timeout=timeout, context=context)
        sock = open_validated_tcp_socket(candidate, timeout)
        try:
            connection.sock = context.wrap_socket(sock, server_hostname=host)
        except Exception:
            sock.close()
            connection.close()
            raise
    else:
        connection = http.client.HTTPConnection(host, port, timeout=timeout)
        connection.sock = open_validated_tcp_socket(candidate, timeout)

    return connection


def perform_security_header_request(
    url: str,
    method: str,
    candidates: list[ConnectCandidate],
) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    request_headers = {
        "User-Agent": "NetworkCheck/1.0",
        "Accept": "*/*",
        "Connection": "close",
        "Host": parsed.netloc,
    }

    if method == "GET":
        request_headers["Range"] = "bytes=0-0"

    last_error: Exception | None = None

    for candidate in candidates:
        connection = None
        response = None
        try:
            connection = _open_http_connection(parsed, candidate, timeout=8)
            connection.request(
                method,
                _request_target(parsed),
                headers=request_headers,
            )
            response = connection.getresponse()
            return {
                "ok": True,
                "status_code": response.status,
                "reason": response.reason,
                "headers": response.headers,
            }
        except Exception as exc:
            last_error = exc
        finally:
            if response is not None:
                response.close()
            if connection is not None:
                connection.close()

    return {
        "ok": False,
        "error": str(last_error or "No validated connection candidates are available."),
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

    candidates = resolved["candidates"]
    request_result = perform_security_header_request(normalized["url"], "HEAD", candidates)
    method_used = "HEAD"

    if request_result["ok"] and request_result.get("status_code") in {405, 501}:
        request_result = perform_security_header_request(normalized["url"], "GET", candidates)
        method_used = "GET"
    elif not request_result["ok"]:
        request_result = perform_security_header_request(normalized["url"], "GET", candidates)
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
