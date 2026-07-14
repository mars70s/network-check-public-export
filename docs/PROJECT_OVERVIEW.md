# Project Overview

## Purpose

Network Check is a lightweight public network and domain diagnostic service.
It displays externally observable information about submitted public targets.
It does not change remote systems.

## Public Features

- Client IPv4 / IPv6 visibility.
- DNS A, AAAA, CNAME, NS, and SOA lookup.
- IPv4-only, IPv6-only, and dual-stack classification.
- DNS response timing.
- IPv4 / IPv6 availability analysis.
- TLS negotiation and certificate information.
- HTTP/2 negotiation visibility.
- MX, SPF, and DMARC lookup.
- PTR reverse lookup.
- CAA lookup.
- Selected HTTP Security headers.
- Domain Multi Check.
- public explanation pages.
- anonymous aggregate usage counters.

## Safety Boundary

- No port scan.
- No vulnerability scan.
- No SMTP authentication test.
- No mail sending.
- No brute force.
- No firewall changes.
- No remote system changes.
- Direct-connect checks reject non-public or special-use destinations before connection.

## Data Position

- Submitted targets and diagnostic results are not saved as public repository data.
- Runtime may store an anonymous daily aggregate counter in SQLite.
- Aggregate records do not contain submitted domain, submitted IP, URL, headers, cookies, User-Agent, client identifier, or diagnostic result.

## Repository Role

This public repository is for portfolio and reference use.
It contains selected public-safe source, docs, templates, static assets, and configuration examples only.
