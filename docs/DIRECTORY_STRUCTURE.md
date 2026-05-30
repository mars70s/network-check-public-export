# Directory Structure

## Recommended Public Repository Structure

    network-check-pub/
    |-- README.md
    |-- LICENSE
    |-- .gitignore
    |-- .env.example
    |-- requirements.txt
    |-- main.py
    |-- templates/
    |   |-- base.html
    |   |-- index.html
    |   |-- domain.html
    |   |-- tls.html
    |   |-- http2.html
    |   |-- dns_timing.html
    |   |-- ip_preference.html
    |   |-- mx.html
    |   |-- spf.html
    |   |-- dmarc.html
    |   |-- privacy.html
    |   |-- terms.html
    |   -- contact.html
    |-- static/
    |   |-- style.css
    |   -- app.js
    -- docs/
        |-- PROJECT_OVERVIEW.md
        |-- PUBLIC_REPOSITORY_POLICY.md
        |-- SECURITY_POLICY.md
        |-- DATA_HANDLING.md
        |-- CHECKS.md
        -- DIRECTORY_STRUCTURE.md

## File Roles

README.md:

- public project overview
- quick usage
- feature summary

LICENSE:

- license terms

.env.example:

- example environment variables
- placeholder values only

requirements.txt:

- Python dependencies

main.py:

- FastAPI application entry point
- diagnostic check implementation
- route definitions

templates/:

- Jinja2 HTML templates

static/:

- CSS and browser-side JavaScript

docs/:

- public-safe project documentation

## Excluded From Public Repository

The public repository should not include:

- private workflow documents
- private roadmap documents
- private current-state notes
- local-only notes
- production-only deployment notes
- real logs
- databases
- secrets
- runtime output files
