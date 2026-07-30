# Directory Structure

```text
network-check-public-export/
|-- README.md
|-- LICENSE
|-- .gitattributes
|-- .gitignore
|-- .env.example
|-- requirements.txt
|-- main.py
|-- apps/
|   |-- __init__.py
|   |-- composition.py
|   '-- doudemoiikedo.py
|-- network_check/
|   |-- __init__.py
|   |-- public_explanations.py
|   |-- usage_metrics.py
|   |-- application/
|   |   |-- __init__.py
|   |   '-- multi_check.py
|   |-- web/
|   |   |-- __init__.py
|   |   |-- api.py
|   |   |-- context.py
|   |   |-- legacy.py
|   |   |-- metrics.py
|   |   |-- multi_check_catalog.py
|   |   '-- public.py
|   '-- checks/
|-- templates/
|-- static/
'-- docs/
    |-- PROJECT_OVERVIEW.md
    |-- PUBLIC_REPOSITORY_POLICY.md
    |-- SECURITY_POLICY.md
    |-- DATA_HANDLING.md
    |-- CHECKS.md
    |-- DIRECTORY_STRUCTURE.md
    '-- images/
        '-- network-check-screenshot.png
```

- Selected application source.
- Configuration examples.
- Jinja2 templates.
- Static assets.
- Public documentation.
- Reviewed visual assets.

## Selected Source Boundary

- `main.py` is a compatibility ASGI entrypoint that imports the selected public application from `apps.doudemoiikedo`.
- `apps/composition.py` builds the shared FastAPI application from selected public routers.
- `network_check/application/` contains UI-independent Multi Check request handling.
- `network_check/web/` contains selected public-safe route adapters and template context helpers.
- `network_check/checks/` contains the selected read-only check implementations used by the public routes and Domain Multi Check.
- Runtime-specific composition roots are excluded from this public repository.
- `network_check/web/metrics.py` is a public-safe variant that keeps the canonical usage metrics route and excludes non-public operational aliases.
- `templates/usage_metrics.html` is a public-safe variant and does not expose runtime-specific names or operational paths.

## Excluded Contents

- Private workflow / Agent docs.
- Task/current-state records.
- Private roadmaps.
- Deployment/runtime plans.
- Investigation/operation reports.
- Private export-control docs.
- Private helper tools.
- Credentials, keys, certificates, and secrets.
- Logs, databases, caches, and runtime output.
- Private hostnames, server paths, and workstation paths.
