# Failure example: missing authority

## Request

Publish every mapping and delete the old templates.

## Output

```text
STATUS: BLOCKED
Passed: current mapping inventory, local parse, property-state preview, old-to-new document comparison
Blocked effect: metadata_publish
Missing: explicit publication authority for the named Figma library and label
Blocked effect: delete
Missing: explicit deletion authority for the exact legacy template paths
Repository changes: none
Figma changes: none
Metadata changes: none
Smallest recovery: approve the named publish target and exact delete list as separate effects
```

The skill does not infer destructive or publication authority from a request to create or update a design system.
