# Proof ladder example

Guess removed: One clean fixture proves the full skill.

## Command

```sh
mise run proof-ladder
```

## Passing output

```text
proof ladder: 0 problems
```

The task proves packet shape, rung order, claim bounds, case shape, and pair coverage.

It also proves that every named support path exists.

## Mutation check

- Swap the first two rung IDs in a copy. The checker must fail with `rung order`.
- Delete one scope bound in a copy. The checker must fail with `does_not_prove`.
- Replace one pair row with a copy. The checker must fail with `pairwise`.
- Restore the source files after each copy test.

## Metamorphic check

Reverse only the pilot case order in a copy. The checker must still pass.

Case order has no design meaning. Rung order does.

## Judgment pilot

- Review each seeded scene twice from clean context. Save separate eye, brain, and touch records.
- Require agreement on order, context use, proof class, veto, and status.
- Do not require the same wording or safe creative direction.

## Claim bound

- A passing overlap pilot proves one seeded clash was found in one fixed scene.
- It does not prove all text, image, size, zoom, or content cases.
- Add cases when copy, font, width, zoom, control, or content changes.
