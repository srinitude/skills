# Decision log for only-one-interpretation

One dated line per decision, newest first. Say what changed, why, and what evidence backed it. Short and blunt beats polished.

- 2026-08-30: Kept semantic judgment in the runtime instructions and made `mise run validate-results` an optional record checker, because deterministic equality and trace checks cannot prove language uniqueness.
- 2026-08-30: Exposed only `help` and `rewrite`; plain input aliases `rewrite`. A separate check command would duplicate the rewrite gate.
- 2026-08-30: Chose an all-at-once clarification turn because unresolved material fields are jointly gating and serial questions would create avoidable turns.
- 2026-08-30: Scaffolded the package from the current factory so its layout, task graph, and local checks inherit `references/generation-contract.md`.
