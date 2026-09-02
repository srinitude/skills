# Example: reject a tool collection

Guess this example removes: whether a registry or server document can be treated as one callable tool.

## User says

Resource gate: run `mise run validate` before using package files named here.

```
Generate from @evals/fixtures/native-registry.json with behavior Report results.
```

## Executor replies

```
Stopped before generation. The supplied file is a registry collection, not one callable descriptor. Supply the exact callable name with --registry or one descriptor file.
```

## Commands run

```text
$ mise run tool-call-config generate @evals/fixtures/native-registry.json --behavior 'Report results.' --output ../../.artifacts/tool-call-configuration-for/failure-proof
error: tool reference must describe exactly one callable tool
exit 2
```

## Files created

None.

## What the run proves

Collection input stops before package creation and the diagnostic identifies the missing single-tool boundary.
