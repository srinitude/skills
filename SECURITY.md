# Security policy

## Supported version

Security fixes target the latest tagged release and `main`.

## Report a problem

Do not open a public issue for a credential leak, path escape, command injection, package traversal, or unsafe plugin action.

Email `kiren@fantasymetals.com` with:

- the affected version or commit;
- the smallest reproduction;
- the expected boundary;
- the observed result;
- any files or commands needed to verify the report.

Do not include unrelated private data or active credentials.

## Security boundaries

The local MCP server is read-only. It rejects absolute paths, traversal, hidden paths, nested references, and symlink escapes. It has no network call, telemetry, credential field, or write tool.

Client manifests contain no secret. Paid evaluation reads credentials from the process environment only after an explicit cost approval step.
