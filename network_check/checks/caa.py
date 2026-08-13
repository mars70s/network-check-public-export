from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver

from .common import DOMAIN_RE, _decode_dns_value, normalize_domain

def check_caa(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0
    resolver.timeout = 2.0

    try:
        answers = resolver.resolve(normalized, "CAA")
        caa_records = []
        for answer in answers:
            flags = getattr(answer, "flags", "")
            tag = _decode_dns_value(getattr(answer, "tag", ""))
            value = _decode_dns_value(getattr(answer, "value", ""))
            caa_records.append({
                "flags": flags,
                "tag": tag,
                "value": value,
                "raw": answer.to_text(),
            })

        caa_records = sorted(caa_records, key=lambda item: item["raw"])

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        caa_records = []
    except Exception:
        return {
            "ok": False,
            "domain": normalized,
            "error": "CAA lookup failed. / CAA確認に失敗しました。",
        }

    if caa_records:
        level = "good"
        status = "CAA record found. / CAAレコードが見つかりました。"
    else:
        level = "warn"
        status = "No CAA record found. / CAAレコードは見つかりませんでした。"

    return {
        "ok": True,
        "domain": normalized,
        "caa_records": caa_records,
        "status": status,
        "level": level,
    }
