from __future__ import annotations

from typing import Any

from .common import DOMAIN_RE, normalize_domain, resolve_records

def check_domain(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    a_records = resolve_records(normalized, "A")
    aaaa_records = resolve_records(normalized, "AAAA")
    cname_records = resolve_records(normalized, "CNAME")
    ns_records = resolve_records(normalized, "NS")
    soa_records = resolve_records(normalized, "SOA")

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

    return {
        "ok": True,
        "domain": normalized,
        "a_records": a_records,
        "aaaa_records": aaaa_records,
        "cname_records": cname_records,
        "ns_records": ns_records,
        "soa_records": soa_records,
        "status": status,
        "message": message,
        "level": level,
    }
