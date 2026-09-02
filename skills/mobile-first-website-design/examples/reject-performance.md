# Reject a performance regression

Run from the skill directory.

## Command

`mise run validate-packet assets/fixtures/fail-performance.json`

## Standard output

`{"errors":["BLOCKED_PERFORMANCE"],"packet_sha256":"d1df616428d7bf3c8b90198e9ca66457b65c4432dc4966787ca30c941c500bcf","status":"BLOCKED_PERFORMANCE"}`

## Standard error

Empty.

## Exit code

`1`
