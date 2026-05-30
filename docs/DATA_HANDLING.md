# Data Handling

## Data Processed

Network Check may process:

- submitted domain names
- DNS query results
- TLS negotiation results
- HTTP/2 negotiation results
- DNS response timing values
- client IP version visible to the application
- User-Agent header
- Accept-Language header

## Persistent Storage

The public design does not require persistent storage of diagnostic results.

Diagnostic results should be generated per request and rendered to the user.

## Logs

Production logs are outside the public repository scope.

Do not commit logs to the public repository.

## Submitted Domains

Submitted domains should be treated as request input.

They should not be stored as public repository data or committed as examples unless replaced with placeholders.

## Example Data

Examples must use synthetic or placeholder values.

Recommended placeholder values:

- example.com
- example.net
- contact@example.com
- 192.0.2.1
- 2001:db8::1

## Future Storage Requirement

If future features require storage, document the following before implementation:

- data source
- storage location
- retention period
- redaction policy
- deletion method
- repository exclusion rule
