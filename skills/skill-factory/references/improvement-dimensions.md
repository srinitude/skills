# Improvement dimensions

Read this entire catalog at initial loading through `mise run improvement-policy`, as directed by [the skill body](../SKILL.md), before the experiment contract in [resource and experiment design](resource-and-experiment-design.md). It extends the existing resource inventory with observable domain qualities. Each ID requires an applicability reason and its source/outcome relationship at the current ledger owner. An unknown measurement is unresolved, never non-use. These are proposed skill-specific operationalizations synthesized from the cited sources, not an exact reproduction of a standard or a universal closed list. Preserve and add all source-required and newly discovered dimensions before acceptance.

Each applicable dimension binds its metric/unit/direction or target range, baseline and candidate, actual population/workload, evaluator, uncertainty, minimum meaningful gain, rejection condition and evidence owner before results are viewed. Keep direct measurements, real task behavior and model/human rubric judgments distinct. Intelligence, creativity and taste have no universal objective scalar; do not invent one. A measured judgment is still judgment. Protect every applicable dimension, including every resource in the existing catalog. One metric can inform several dimensions without becoming independent evidence twice. Numbers in Basis refer to the source notes below; precise metrics require domain validation.

| ID | Dimension | Example measurable evidence and direction | Basis |
| --- | --- | --- | --- |
| Q01 | Intended outcome effectiveness | Higher accepted end-to-end task success, with all mandatory conditions met | Skill contract; 7 |
| Q02 | Functional completeness | Higher coverage of actual required operations, exceptions and outputs; missing mandatory behavior is a gate | Skill contract; 11 |
| Q03 | Correctness | Lower independently detected factual, logical, numerical and execution error rates | 5, 6 |
| Q04 | Grounding and source fidelity | Higher supported-claim precision and required-evidence recall; lower stale or misattributed claims | Skill contract; 6 |
| Q05 | Instruction and constraint fidelity | Lower omitted, weakened, invented or violated requirements | Skill contract |
| Q06 | Relevance and domain fit | Higher useful output acceptance on the actual domain task; lower irrelevant work | Skill contract; 7 |
| Q07 | Reasoning and problem solving | Higher held-out multi-step task success with valid derivations and effects | 5, 7 |
| Q08 | Planning and dependency handling | Fewer invalid prerequisite uses, needless replans and dead ends per accepted outcome | Skill contract |
| Q09 | Tool and interface competence | Higher correct tool selection, argument forwarding, parsing and real consumer success | 7 |
| Q10 | Calibration and uncertainty handling | Lower calibration error and unsupported certainty; valid abstention and escalation | 5, 6 |
| Q11 | Generalization and transfer | Smaller performance loss on held-out projects, task families and unfamiliar valid inputs | 5, 6 |
| Q12 | Learning from corrections | Lower recurrence of the same defect on later comparable invocations | Skill contract |
| Q13 | Deterministic mechanics | Higher exact repeated results for fully captured deterministic inputs | 12 |
| Q14 | Reproducibility | Higher independently repeated build and behavior agreement under declared conditions | 12 |
| Q15 | Reliability across trials | Higher all-trial success; lower retry-selected-only success, flakes and failure recurrence | 6, 7 |
| Q16 | Perturbation tolerance | Higher valid outcomes under typos, ordering changes, missing optional inputs and benign variations | 5, 6 |
| Q17 | Fault tolerance | Higher preserved valid behavior under injected dependency or service failures | 6 |
| Q18 | Recoverability | Lower time and data loss to restore a verified usable state | 6; skill contract |
| Q19 | Idempotence and replay safety | Fewer duplicate effects and divergences after retries or resumes | Skill contract |
| Q20 | Concurrency and state integrity | Fewer races, lost updates, stale reads and invalid simultaneous effects | Skill contract |
| Q21 | Availability and readiness | Higher successful consumer readiness within the declared operating window | 6, 13 |
| Q22 | End-to-end speed | Lower accepted-outcome wall time, including mandatory reading, setup, trials, failures and proof | 7, 13 |
| Q23 | Responsiveness and tail latency | Lower time to a useful first result and p95/p99 completion latency | 13 |
| Q24 | Throughput and scalability | Higher accepted outcomes per interval; lower growth of time and memory with workload size | 13 |
| Q25 | CPU efficiency | Lower user/system CPU seconds per accepted outcome | Existing resource catalog |
| Q26 | Memory efficiency | Lower peak and retained memory, allocations, paging and swap | Existing resource catalog |
| Q27 | Storage efficiency | Lower artifact/temp footprint and read/write operations without deleting required evidence | Existing resource catalog |
| Q28 | Network efficiency | Lower requests, transferred bytes, retries and rate-limit waste | Existing resource catalog |
| Q29 | Context and token efficiency | Lower total tokens and repeated loads while preserving all required context and reads | Existing resource catalog |
| Q30 | Cache correctness and efficiency | Lower recomputation cost with no stale-result acceptance; cold/warm cases separated | Existing resource catalog |
| Q31 | Orchestration efficiency | Lower launch, queue, serialization, contention and idle time | Existing resource catalog |
| Q32 | Accelerator efficiency | Lower device time/memory per accepted outcome when a device is used | Existing resource catalog |
| Q33 | Energy and environmental efficiency | Lower measured energy or supported emissions estimate per accepted outcome, with system boundary disclosed | Domain extension |
| Q34 | Monetary efficiency | Lower complete API/compute/storage/transfer cost per accepted outcome, including failed trials | 7; resource catalog |
| Q35 | Human effort efficiency | Lower completion/review/correction time and avoidable interruptions for the actual recipient | Skill contract; 13 |
| Q36 | Safety | Gate on prohibited harm; lower incidence and severity of domain-specific hazards | 6 |
| Q37 | Security | Gate on authority boundaries; fewer exploitable injection, access and integrity failures | 6 |
| Q38 | Privacy and data minimization | Fewer unauthorized disclosures and unnecessary sensitive data retention or transfers | 6 |
| Q39 | Human control and approval fidelity | No forged, bypassed or stale approvals; successful pause, correction and cancellation | Skill contract; 6 |
| Q40 | Fairness and harmful-bias control | Lower relevant subgroup error disparities and harmful differential treatment under justified measures | 5, 6 |
| Q41 | Transparency and provenance | Higher traceability from claims/effects to actual inputs, versions and responsible decisions | 6 |
| Q42 | Explainability and interpretability | Higher recipient ability to understand operation, meaning and limitations, tested separately | 6 |
| Q43 | Observability and diagnosability | Lower time to locate the actual failed owner; higher useful fault-detection precision/recall | 13 |
| Q44 | Accessibility and inclusion | Fewer applicable accessibility failures; higher actual task success with required assistive modes | 14 |
| Q45 | Comprehension and plain language | Higher accurate reader understanding; fewer ambiguities and clarification cycles | Skill contract |
| Q46 | Usability and error prevention | Higher unaided task completion; fewer user errors and costly recoveries | Skill contract |
| Q47 | Learnability and retention | Faster correct first use and stronger later recall/transfer, when learning is an outcome | Domain extension |
| Q48 | Cognitive load and interaction burden | Lower observed effort, avoidable decisions and context switching, without removing useful learning | Domain extension |
| Q49 | Appropriate trust and expectation fit | Better alignment between perceived and demonstrated capability, with failures understood | 6 |
| Q50 | Recipient usefulness and adoption | Higher actual useful downstream use; lower transferred checking and repair work | Skill contract |
| Q51 | Creativity and originality | More independently judged novel, useful, constraint-valid alternatives | Skill contract; judgment evidence |
| Q52 | Diversity and exploratory range | Broader meaningful valid approaches without forced sameness or arbitrary variation | Skill contract; judgment evidence |
| Q53 | Craft, aesthetics and sensory quality | Better medium-specific artifact assessments or instrument results under a declared rubric | Skill contract; actual sensory evidence |
| Q54 | Semantic judgment and contextual suitability | Higher agreement among qualified reviewers on context-sensitive choices, with disagreements retained | Skill contract; judgment evidence |
| Q55 | Maintainability and modifiability | Lower demonstrated time and defect rate for representative future changes | 11; skill contract |
| Q56 | Simplicity and ownership clarity | Fewer competing owners and unnecessary concepts with unchanged capability | Skill contract |
| Q57 | Testability and evaluator quality | Higher detection of known defects; lower false acceptance/rejection; protected evaluator integrity | 7, 9 |
| Q58 | Dependency and installation quality | Fewer unnecessary dependencies, compatibility failures and unreproducible setups | Skill contract; 12 |
| Q59 | Portability and interoperability | Higher success across declared environments, projects and public interfaces | Skill contract |
| Q60 | Extensibility and composability | Lower verified integration effort with preserved schemas, boundaries and error semantics | Skill contract |
| Q61 | Version and migration safety | Higher successful compatible upgrades and conflict-preserving restoration | 15, 16 |
| Q62 | Reuse and propagation fidelity | Higher correct independent generated/updated outputs with no stale policy copies | Skill contract |
| Q63 | Evidence and research efficiency | More validated useful improvements per total research cost, with all failed trials included | Proposed extension of 2, 7 |
| Q64 | Sustainability of maintenance | Lower recurring repair burden and fewer unsupported owners or expired dependencies | Skill contract |

## Evaluation basis

The inspected training loop excludes initial steps from its timer and checks the threshold after a step; startup and evaluation add elapsed time. Its evaluator also receives candidate-controlled batch size and model output. Freeze and inspect actual evaluator inputs and results instead of assuming that a source-file digest or advertised duration proves comparability. Read the pinned implementation before transferring its mechanism. [Training source](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/train.py), [evaluation source](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/prepare.py).

Adaptive reuse can overfit confirmation cases. Retain case-exposure history, independent confirmation and fixed sampling/stopping rules; use a justified sequential method only when its assumptions fit. Do not repeatedly peek at fixed-sample intervals until a favorable result appears. Resource limits, concurrency and service noise are experimental conditions, not ignorable setup. [Holdout research](https://arxiv.org/abs/1506.02629v2), [confidence-sequence research](https://arxiv.org/abs/1810.08240), [infrastructure experiments](https://www.anthropic.com/engineering/infrastructure-noise).

## Source notes

1: Andrej Karpathy, [autoresearch README, inspected revision](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/README.md), retrieved 2026-09-10. Primary implementation context. 2: Andrej Karpathy, [autoresearch program.md, inspected revision](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md), retrieved 2026-09-10. Primary experiment instructions. 3: Andrej Karpathy, [autoresearch train.py, inspected revision](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/train.py#L499-L582), retrieved 2026-09-10. Primary timing and training implementation. 4: Andrej Karpathy, [autoresearch prepare.py, inspected revision](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/prepare.py#L310-L332), retrieved 2026-09-10. Primary evaluation implementation. 5: Rishi Bommasani, Percy Liang and Tony Lee, [HELM multi-metric evaluation research](https://crfm.stanford.edu/2022/11/17/helm.html), Stanford CRFM, 2022-11-17. Original research overview; historical framework, not current model rankings. 6: NIST, [AI Risks and Trustworthiness](https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/), AI RMF 1.0, 2023. Primary framework; the page states an update is in progress. 7: Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), 2026-01-09. First-party engineering experience. 8: Gian Segato, [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise), Anthropic, 2026-02-05. Original bounded experiments; environment-specific results. 9: Cynthia Dwork and colleagues, [Generalization in Adaptive Data Analysis and Holdout Reuse](https://arxiv.org/abs/1506.02629v2), 2015. Original research on adaptive reuse and its assumptions. 10: Steven Howard and colleagues, [Time-uniform, nonparametric, nonasymptotic confidence sequences](https://arxiv.org/abs/1810.08240), 2021 publication. Original statistical methods; assumptions must be established before use. 11: ISO, [ISO/IEC 25010:2023 public abstract](https://www.iso.org/standard/78176.html), 2023-11. Nine-characteristic product quality model; full standard not inspected. 12: Reproducible Builds, [Definitions](https://reproducible-builds.org/docs/definition/), retrieved 2026-09-10. Primary definition of reproducible build conditions and artifacts. 13: Rob Ewaschuk, [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/), Google SRE. Primary operational guidance on latency, traffic, errors, saturation and useful monitoring. 14: W3C, [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/), current page retrieved 2026-09-10. Normative guidance for applicable web outputs; not a universal agent evaluation standard. 15: Git project, [git-revert](https://git-scm.com/docs/git-revert), retrieved 2026-09-10. Primary version-control contract. 16: Git project, [git-restore](https://git-scm.com/docs/git-restore), retrieved 2026-09-10. Primary path restoration contract.
