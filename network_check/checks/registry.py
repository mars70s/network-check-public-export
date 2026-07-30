from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from network_check.checks.caa import check_caa
from network_check.checks.dns import check_domain
from network_check.checks.dns_timing import check_dns_timing
from network_check.checks.http2 import check_http2
from network_check.checks.ip_preference import check_ip_preference
from network_check.checks.mail import (
    check_dmarc_records,
    check_mx_records,
    check_spf_records,
)
from network_check.checks.tls import check_tls


DomainCheckFunction = Callable[[str], dict[str, Any]]
CheckInputContract = Literal["domain"]


@dataclass(frozen=True)
class CheckRegistryEntry:
    """Stable UI-independent definition of one domain-based Multi Check."""

    check_id: str
    input_contract: CheckInputContract
    function: DomainCheckFunction


MULTI_CHECK_REGISTRY: tuple[CheckRegistryEntry, ...] = (
    CheckRegistryEntry("domain", "domain", check_domain),
    CheckRegistryEntry("ip_preference", "domain", check_ip_preference),
    CheckRegistryEntry("dns_timing", "domain", check_dns_timing),
    CheckRegistryEntry("tls", "domain", check_tls),
    CheckRegistryEntry("http2", "domain", check_http2),
    CheckRegistryEntry("mx", "domain", check_mx_records),
    CheckRegistryEntry("spf", "domain", check_spf_records),
    CheckRegistryEntry("dmarc", "domain", check_dmarc_records),
    CheckRegistryEntry("caa", "domain", check_caa),
)

# This preserves the current deterministic batch execution and result insertion
# order. It is not UI display order; UI ordering belongs to the UI catalog.
MULTI_CHECK_EXECUTION_ORDER: tuple[str, ...] = tuple(
    entry.check_id for entry in MULTI_CHECK_REGISTRY
)

MULTI_CHECK_FUNCTIONS: dict[str, DomainCheckFunction] = {
    entry.check_id: entry.function for entry in MULTI_CHECK_REGISTRY
}

MULTI_CHECK_INPUT_CONTRACTS: dict[str, CheckInputContract] = {
    entry.check_id: entry.input_contract for entry in MULTI_CHECK_REGISTRY
}