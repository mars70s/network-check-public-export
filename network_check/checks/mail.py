from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver

from .common import DOMAIN_RE, normalize_domain

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
