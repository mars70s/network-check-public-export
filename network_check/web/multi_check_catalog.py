from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MultiCheckCatalogEntry:
    """UI metadata for one stable Multi Check ID."""

    check_id: str
    label: str
    category: str
    category_label: str
    description: str
    default_selected: bool
    ui_order: int


MULTI_CHECK_UI_CATALOG: tuple[MultiCheckCatalogEntry, ...] = (
    MultiCheckCatalogEntry(
        "domain",
        "Domain",
        "dns",
        "DNS",
        "A / AAAA / CNAME / NS / SOA",
        True,
        10,
    ),
    MultiCheckCatalogEntry(
        "ip_preference",
        "IP Preference",
        "ip",
        "IP",
        "IPv4 / IPv6 availability",
        True,
        90,
    ),
    MultiCheckCatalogEntry(
        "dns_timing",
        "DNS Timing",
        "dns",
        "DNS",
        "A / AAAA response timing",
        False,
        20,
    ),
    MultiCheckCatalogEntry(
        "tls",
        "TLS",
        "web",
        "WEB",
        "Certificate and cipher",
        False,
        70,
    ),
    MultiCheckCatalogEntry(
        "http2",
        "HTTP/2",
        "web",
        "WEB",
        "HTTPS negotiation",
        False,
        80,
    ),
    MultiCheckCatalogEntry(
        "mx",
        "MX",
        "mail",
        "MAIL",
        "Mail exchanger records",
        True,
        40,
    ),
    MultiCheckCatalogEntry(
        "spf",
        "SPF",
        "mail",
        "MAIL",
        "Sender policy TXT",
        True,
        50,
    ),
    MultiCheckCatalogEntry(
        "dmarc",
        "DMARC",
        "mail",
        "MAIL",
        "Mail authentication policy",
        True,
        60,
    ),
    MultiCheckCatalogEntry(
        "caa",
        "CAA",
        "dns",
        "DNS",
        "Certificate authority policy",
        False,
        30,
    ),
)


def multi_check_ui_options() -> list[dict[str, Any]]:
    """Return the legacy template projection without executable check objects."""

    return [
        {
            "id": entry.check_id,
            "label": entry.label,
            "category": entry.category,
            "category_label": entry.category_label,
            "description": entry.description,
            "default_selected": entry.default_selected,
            "ui_order": entry.ui_order,
        }
        for entry in sorted(MULTI_CHECK_UI_CATALOG, key=lambda entry: entry.ui_order)
    ]