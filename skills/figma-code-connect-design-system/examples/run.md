# Run example

## Request

Create the approved tablet checkout design system from a PRD, two reference images, and an empty repository. Build one vertical slice first. Do not publish mappings until I approve the preview.

## Result shape

```text
STATUS: STALE
Mode: create
Target: tablet checkout
Completed: intake, source audit, product model, screen inventory, inspected repository, DTCG token proof, first atom and molecule
Repository changes: authorized token files, component source, tests, and one Button.figma.ts template
Figma changes: authorized variables, Button component set, field molecule, and checkout template slice
Metadata changes: none; publish permission is not granted
Display/context: local Code Connect preview passed; Dev Mode and MCP remain unproved until publication
Stale: checkout template and screen after the field molecule spacing repair
Next action: rebuild the affected template and screen, recheck pixels, then request mapping-publication authority
```

The run does not claim `PASS` while a dependent screen is stale.
