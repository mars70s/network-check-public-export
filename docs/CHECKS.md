# Checks

## Client Information

- Purpose: show the client IPv4 / IPv6 information visible to the application.
- Route: / and related public pages.
- Boundary: displays request-visible information only.

## Domain Check

- Purpose: resolve DNS A, AAAA, CNAME, NS, and SOA records.
- Route: /domain.
- Boundary: DNS lookup only; no remote system change.

## DNS Timing

- Purpose: measure DNS response timing.
- Route: /dns-timing.
- Boundary: DNS timing only.

## IPv4 / IPv6 Preference

- Purpose: classify IPv4-only, IPv6-only, and dual-stack availability.
- Route: /ip-preference.
- Boundary: uses observable DNS/address behavior.

## TLS Check

- Purpose: show TLS negotiation and certificate information.
- Route: /tls.
- Boundary: uses the standard TLS port only; validates that the resolved destination is public before connection; not a vulnerability scan.

## HTTP/2 Check

- Purpose: show HTTP/2 negotiation visibility.
- Route: /http2.
- Boundary: validates that the resolved destination is public before connection; checks negotiation through runtime curl capability; displays the effective requested URL; does not automatically follow redirects; does not crawl.

## MX Check

- Purpose: show mail exchanger records.
- Route: /mx.
- Boundary: DNS lookup only; no SMTP authentication test and no mail sending.

## SPF Check

- Purpose: show SPF-related DNS TXT policy.
- Route: /spf.
- Boundary: DNS lookup only.

## DMARC Check

- Purpose: show DMARC policy records.
- Route: /dmarc.
- Boundary: DNS lookup only.

## PTR Check

- Purpose: show PTR reverse lookup information.
- Route: /ptr.
- Boundary: reverse DNS lookup only.

## CAA Check

- Purpose: show CAA records.
- Route: /caa.
- Boundary: DNS lookup only.

## Security Headers Check

- Purpose: show selected HTTP Security Headers.
- Route: /security-headers.
- Boundary: accepts public HTTP/HTTPS URL only; rejects embedded credentials; rejects non-default port; rejects localhost, private, reserved, and non-public target before connection; does not automatically follow redirects; displays selected response headers only.

## Domain Multi Check

- Purpose: combine selected domain checks.
- Route: /multi-check.
- Boundary: preserves each individual result boundary; excludes PTR input and URL-based Security Headers input.

## Public Explanation Pages

- Purpose: provide public explanation content for checks.
- Route: public explanation routes.
- Boundary: documentation content only.
