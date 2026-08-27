# DTCG Transfer And Experiment Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Transfer And Experiment Contracts.

Load trigger: Use this appendix while implementing or reviewing `references/creative-transfer.md`, `assets/experiment-contract.json`, `references/experimental-decision.md`, Step 08, `E_TRANSFER`, `E_EXPERIMENT`, `E_EXPLORATION`, or their tests. Package files own runtime procedure. This appendix owns the approved transfer and experiment design.

## Transfer Contract

Every transfer records:

- `source_id` and source domain
- target decision and exact token paths
- preserved relational structure
- forbidden surface traits
- predicted visual, behavioral, or physical effect
- baseline and matched alternative
- falsifier and stop rule
- proof regions and final disposition

Reject a transfer when it copies a motif, has no visual or behavioral result, cannot be falsified, lacks a source relation, or exists only to fill a quota.

## Experiment Contract

Exploration and confirmation are separate. Before confirmation, freeze:

- question, hypothesis, and null
- mechanism and source relations
- primary change or factorial declaration
- independent, held, nuisance, and blocked variables
- baseline, controls, run order, and sample contexts
- token paths, states, viewports, inputs, and interactions
- predicted results, risks, and uncertainty
- objective measures and qualitative vision questions
- vetoes, thresholds, stop rule, evidence plan, and rollback

Confirmation cannot change the frozen question, prediction, measure, or threshold after seeing the result. A changed field creates a new experiment ID.

## Method Choice

| Condition                                     | Required method                                                                |
| --------------------------------------------- | ------------------------------------------------------------------------------ |
| A few factors may interact.                   | Full factorial comparison.                                                     |
| Many factors need early reduction.            | Screening design.                                                              |
| A continuous space may curve.                 | Response-surface design.                                                       |
| A large continuous space lacks a known shape. | Space-filling design.                                                          |
| Context may change the result.                | Block by viewport, theme, state, input, interaction, or rendering environment. |

The record states why the method fits the question. An experiment cannot pass only because it used a named method.

## Retention

The final token set retains at least three experimental tokens from three mechanism families. At least one uses inversion or an antithetical thesis. Each retained token traces through the candidate, transfer, experiment, evidence, proof specimen, final visual review, and claim boundary.

An experimental token may remain with no passing use claim when its limits are explicit. It cannot satisfy a production, accessibility, source-fit, or originality claim that its evidence does not support.

## Failure And Tests

Return `BLOCKED: E_TRANSFER` for a copied surface trait, missing source relation, absent prediction, absent falsifier, or quota-only transfer. Return `BLOCKED: E_EXPERIMENT` for an incomplete or changed frozen record. Return `BLOCKED: E_EXPLORATION` when the final token set lacks the required count, mechanism spread, inversion, lineage, or visible specimens.

Focused tests must reject surface imitation, one-variable claims with an undeclared interaction, thresholds selected after the result, an unmatched baseline, missing viewport or input blocks, a retained experiment with no token path, and experimental-token drift. A positive fixture must reproduce its run order and trace three retained tokens from distinct mechanisms through current final bytes.

## Research Owner

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) owns the dated creativity, experiment-design, analogy, and falsification evidence that supports these contracts.
