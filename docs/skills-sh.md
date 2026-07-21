# skills.sh publishing notes

The canonical source is [`srinitude/skills`](https://github.com/srinitude/skills). Its directory page is [`skills.sh/srinitude/skills`](https://skills.sh/srinitude/skills).

## Install and discovery

Install from the GitHub source:

```sh
npx skills add srinitude/skills
```

List the available skills without installing them:

```sh
npx skills add srinitude/skills --list
```

skills.sh listings appear automatically after people install a source with the skills CLI. The CLI reports the source, skill files, and timestamp as anonymous telemetry. It doesn't report personal or device information.

Set `DISABLE_TELEMETRY=1` to opt out. `DO_NOT_TRACK=1` is also supported by the upstream CLI.

## Badge

The repository README uses the source badge documented by skills.sh:

```md
[![skills.sh](https://skills.sh/b/srinitude/skills)](https://skills.sh/srinitude/skills)
```

## Catalog API

The catalog API is served from `https://skills.sh/api/v1/`. API consumers deployed on Vercel authenticate with a short-lived `VERCEL_OIDC_TOKEN`. Request handlers should read or obtain a fresh token for each request instead of caching it at module scope.

Use the stable `{source}/{slug}` ID returned by the API for skill lookups. Respect response cache headers and the `Retry-After` header on HTTP 429 responses. This repository doesn't call the catalog API today.

## Listing corrections

Listing corrections aren't handled by the install CLI or the public catalog API. Open an issue or pull request in [`vercel-labs/skills`](https://github.com/vercel-labs/skills) with:

- every stale skills.sh URL;
- the replacement URL;
- repository evidence for the move or deletion;
- the date the old and replacement listings were verified.

Keep a listing cleanup separate from unrelated documentation or format changes.

## Security

Review a skill before installing it. Report malicious listings through [Vercel's security process](https://security.vercel.com/). Report repository-specific bugs through this repository's [support path](../SUPPORT.md).

## Sources

- [Documentation](https://www.skills.sh/docs)
- [CLI reference](https://www.skills.sh/docs/cli)
- [API reference](https://www.skills.sh/docs/api)
- [FAQ](https://www.skills.sh/docs/faq)
