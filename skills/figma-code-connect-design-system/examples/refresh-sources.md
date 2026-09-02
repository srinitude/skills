# Refresh sources example

## Request

Refresh the source boundary and report drift. Do not edit the package.

## Output

```text
Retrieved: 2026-08-31
Capability schemas: inspected
Code Connect package: 2.0.0
Repository tag: f55fc3a8d9392df0dd80a9e859ffdddbd5c50019
Agent Skills specification: reachable
Registry commit: a80a9f88b6b72c6358f6101e53aed64ed715058a
Drift affecting behavior: none found
Package changes: none
```

If drift exists, the command returns affected claims and proposed package files but does not edit them without a separate request.
