# Checks

## Overview

Network Check provides lightweight public network diagnostic checks.

Each check is intended to be read-only and externally observable.

## Client Information

Purpose:

- display client IP version
- display User-Agent
- display Accept-Language

Route:

- /

## Domain Check

Purpose:

- resolve DNS A records
- resolve DNS AAAA records
- classify IPv4-only, IPv6-only, dual-stack, or unavailable state

Route:

- /domain

## TLS Check

Purpose:

- connect to port 443
- display negotiated TLS version
- display cipher information

Route:

- /tls

Boundary:

- no vulnerability scan
- no certificate attack testing
- no broad port probing

## HTTP/2 Check

Purpose:

- check HTTP/2 negotiation
- display HTTP status code
- display final URL after redirects

Route:

- /http2

Boundary:

- uses runtime HTTP client capability
- does not crawl the site

## DNS Timing

Purpose:

- measure DNS A response timing
- measure DNS AAAA response timing
- display timing in milliseconds

Route:

- /dns-timing

Boundary:

- timing values are runtime reference values
- timing values are not full performance benchmarks

## IPv4 / IPv6 Preference

Purpose:

- inspect A and AAAA availability
- classify IP version availability

Route:

- /ip-preference

Boundary:

- based on DNS record availability
- does not measure real browser route selection

## MX Check

Purpose:

- resolve MX records
- display priority
- display mail exchanger host

Route:

- /mx

Boundary:

- no SMTP connection test
- no mail sending test
- no authentication test

## SPF Check

Purpose:

- resolve TXT records
- extract records starting with v=spf1

Route:

- /spf

Boundary:

- does not fully evaluate SPF policy
- does not send mail

## DMARC Check

Purpose:

- resolve TXT records for _dmarc domain
- extract records starting with v=DMARC1

Route:

- /dmarc

Boundary:

- does not fully evaluate DMARC policy
- does not send mail
- does not test report delivery
