# Security Policy

## Supported Scope

Network Check is a read-only diagnostic service.

It checks externally observable DNS, TLS, HTTP/2, and mail-related DNS records.

## Security Boundary

The application must not modify:

- firewall rules
- fail2ban configuration
- systemd services
- DNS configuration
- mail server configuration
- remote systems

## Sensitive Information

Do not commit:

- .env files
- API keys
- tokens
- passwords
- private keys
- private certificates
- logs
- databases
- captured traffic
- private hostnames
- internal IP inventories
- production deployment notes

## Diagnostic Safety

The project must avoid intrusive behavior.

Disallowed activities:

- port scanning
- vulnerability scanning
- brute-force testing
- SMTP authentication testing
- mail sending tests
- large-scale crawling
- long-term storage of submitted targets

## Reporting Security Issues

If a security issue is found, report it without including sensitive production details.

Use minimal reproduction information and avoid publishing secrets, private hostnames, private IP addresses, or real operational data.
