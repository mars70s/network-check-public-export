# Public Repository Policy

## Purpose

This document defines the public repository boundary for Network Check.

The public repository must be safe to publish and must not expose private runtime information, local development paths, production URLs, secrets, logs, or operational notes.

## Public Repository Role

The public repository contains:

- public-safe source code
- public README
- public documentation
- example environment configuration
- static assets
- templates

The public repository must not contain:

- private git history
- production logs
- databases
- private deployment notes
- real server paths
- real local workstation paths
- real production URLs
- credentials
- API keys
- tokens
- private certificates
- private keys

## Source Boundary

The public repository is generated from selected files only.

It must not be created by directly copying the full private repository.

## Allowed Diagnostic Behavior

Network Check may perform:

- DNS lookups
- TLS connection checks to port 443
- HTTP/2 negotiation checks
- display of client request metadata visible to the application
- rendering of diagnostic results in HTML

## Disallowed Behavior

Network Check must not perform:

- port scanning
- vulnerability scanning
- SMTP authentication tests
- mail sending tests
- brute-force tests
- crawling unrelated URLs
- firewall modification
- fail2ban modification
- systemd modification
- persistent storage of submitted domains as production logs

## Placeholder Policy

Use placeholders in public documentation.

Recommended placeholders:

- example.com
- contact@example.com
- https://example.com/network-check/
- /path/to/network-check
- Network Check Project

## Release Safety

Before publishing, confirm that no private path, hostname, server URL, token, key, certificate, log, database, or operational note exists in the public repository.
