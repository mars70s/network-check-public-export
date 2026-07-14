from __future__ import annotations

import re

from typing import Any

import dns.exception
import dns.resolver

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}\.?$")

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

def _decode_dns_value(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)
