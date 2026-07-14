# Data Handling

## Request Data

The application may process the following request-time data:

- Submitted domain.
- Submitted single IP.
- Submitted public HTTP/HTTPS URL.
- DNS results.
- TLS/HTTP negotiation results.
- Selected HTTP response headers.
- DNS response timing.
- Client request metadata visible to the application.

## Diagnostic Results

diagnostic results are generated per request.
They are not stored as submitted-target history.

## Aggregate Counter Prohibition

Aggregate records must not store:

- Submitted domains.
- Submitted IPs.
- Submitted URLs.
- Request bodies.
- Cookies.
- User-Agent.
- Client identifiers.
- Resolved-address lists.
- diagnostic results.

## Anonymous Aggregate Counters

Runtime may store anonymous daily aggregate counters with these fields:

- Event date.
- Internal event type.
- Internal target identifier.
- Count.
- Update timestamp.

These aggregate fields do not identify a submitted target or user.

## Runtime Database

The aggregate counter database is runtime data.
It may use SQLite, but it must not be committed to the public repository.
It must not be included in release artifacts.
It must not be published as example diagnostic data.

## Logs

Production logs are outside public repository scope.
They must not be committed.

## Example Data

- example.com
- example.net
- contact@example.com
- 192.0.2.1
- 2001:db8::1

## Future Data Changes

New stored fields require prior documentation of:

- Source.
- Fields.
- Retention.
- Redaction.
- Deletion.
- Repository exclusion.
