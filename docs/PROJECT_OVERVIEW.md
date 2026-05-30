# Project Overview

## Purpose

Network Check is a lightweight public network diagnostic service.

It helps users inspect externally observable network and domain configuration information.

## Scope

This project focuses on:

- client IPv4 / IPv6 visibility
- DNS A / AAAA lookup
- dual-stack classification
- TLS version and cipher visibility
- HTTP/2 negotiation visibility
- DNS response timing
- IPv4 / IPv6 availability preference
- MX record lookup
- SPF record lookup
- DMARC record lookup

## Out of Scope

This project does not provide:

- port scanning
- vulnerability scanning
- SMTP login testing
- mail sending tests
- brute-force testing
- firewall management
- fail2ban management
- persistent monitoring
- long-term diagnostic result storage

## Design Position

Network Check is designed as a read-only diagnostic application.

It observes public-facing network configuration but does not modify remote systems, local firewall rules, systemd services, or mail configuration.

## Repository Role

This public repository is intended for portfolio and reference use.

It contains public-safe source code, documentation, and configuration examples only.
