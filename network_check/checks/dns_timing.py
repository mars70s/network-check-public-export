from __future__ import annotations

import time

from typing import Any

import dns.exception
import dns.resolver

from .common import DOMAIN_RE, normalize_domain

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
    ):
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "record_type": record_type,
            "records": [],
            "elapsed_ms": elapsed_ms,
            "error": "DNS query failed. / DNS問い合わせに失敗しました。",
        }
    except Exception:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ok": False,
            "record_type": record_type,
            "records": [],
            "elapsed_ms": elapsed_ms,
            "error": "DNS query failed. / DNS問い合わせに失敗しました。",
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
