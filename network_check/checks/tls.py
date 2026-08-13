from __future__ import annotations

import ssl
from datetime import datetime, timezone

from typing import Any

from .common import DOMAIN_RE, normalize_domain
from .destination_guard import (
    assert_public_connect_target,
    build_blocked_target_result,
    open_validated_tcp_socket,
)

TLS_TCP_CONNECT_TIMEOUT = 5.0


def format_cert_name(name: tuple[Any, ...]) -> str:
    parts: list[str] = []
    for group in name:
        for key, value in group:
            parts.append(f"{key}={value}")
    return ", ".join(parts) if parts else "Unknown"

def check_tls(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    guard_result = assert_public_connect_target(normalized, 443)
    if not guard_result["ok"]:
        return build_blocked_target_result(normalized, guard_result, "tls")

    try:
        context = ssl.create_default_context()
        last_error: Exception | None = None

        for candidate in guard_result["candidates"]:
            sock = None
            try:
                sock = open_validated_tcp_socket(candidate, timeout=TLS_TCP_CONNECT_TIMEOUT)
                tls_sock = context.wrap_socket(sock, server_hostname=normalized)
                sock = None
                with tls_sock:
                    tls_version = tls_sock.version()
                    cipher = tls_sock.cipher()
                    cert = tls_sock.getpeercert()
                break
            except Exception as exc:
                last_error = exc
            finally:
                if sock is not None:
                    sock.close()
        else:
            if last_error is not None:
                raise last_error
            raise OSError("No validated connection candidates are available.")

        not_after = cert.get("notAfter")
        expires_at = "Unknown"
        remaining_days: int | str = "Unknown"

        if not_after:
            expires_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            remaining_days = (expires_dt - now).days
            expires_at = expires_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

        issuer = format_cert_name(cert.get("issuer", ()))
        subject = format_cert_name(cert.get("subject", ()))
        san_entries = [
            value
            for key, value in cert.get("subjectAltName", [])
            if key.lower() == "dns"
        ]

        if tls_version == "TLSv1.3":
            level = "good"
            status = "Modern TLS / 新しいTLS"
        elif tls_version == "TLSv1.2":
            level = "warn"
            status = "TLS 1.2 / TLS 1.2"
        else:
            level = "bad"
            status = "Legacy TLS / 古いTLS"

        if isinstance(remaining_days, int) and remaining_days < 15:
            level = "bad"
            status = "Certificate expires soon. / 証明書の期限が近づいています。"
        elif isinstance(remaining_days, int) and remaining_days < 30 and level == "good":
            level = "warn"
            status = "Certificate renewal should be checked. / 証明書更新の確認を推奨します。"

        return {
            "ok": True,
            "domain": normalized,
            "tls_version": tls_version,
            "cipher": cipher[0] if cipher else "Unknown",
            "cipher_protocol": cipher[1] if cipher else "Unknown",
            "cipher_bits": cipher[2] if cipher else "Unknown",
            "certificate_expires_at": expires_at,
            "certificate_remaining_days": remaining_days,
            "certificate_issuer": issuer,
            "certificate_subject": subject,
            "certificate_san": san_entries,
            "status": status,
            "level": level,
        }

    except Exception:
        return {
            "ok": False,
            "domain": normalized,
            "error": "TLS connection failed. / TLS接続に失敗しました。",
        }
