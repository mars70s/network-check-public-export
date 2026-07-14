from __future__ import annotations

from typing import Any

from .common import DOMAIN_RE, normalize_domain, resolve_records

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
