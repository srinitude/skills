"""Own the safe Figma skill change record."""

RESOURCES = ["time", "cpu", "memory", "storage", "network", "cache",
             "context", "process", "concurrency", "accelerator", "cost",
             "human_attention"]
PROTECTED = ["correctness", "wall_clock_time", "deterministic_coverage",
             "task_success", "safety", "portability", "token_efficiency",
             "creative_range", "experimental_range", "exploratory_range",
             "semantic_judgment", "visual_judgment", "maintainability",
             "simplicity", "plain_language", "current_skill_contract"]
EVIDENCE = ["baseline_content_digest", "candidate_content_digest",
            "named_dimension", "frozen_evaluator_digest", "environment_receipt",
            "baseline_results", "candidate_results", "protected_dimension_results",
            "elapsed_seconds", "applicable_resource_results",
            "not_applicable_resource_reasons", "status",
            "restoration_receipt_when_rejected"]


def improvement_contract():
    return {"version": "1.1.0", "mode": "optional_final_step",
        "cli_owner": "mise",
        "baseline": {"source": "fresh_last_accepted_version",
                     "freeze_before_trial": True},
        "evaluator": {"freeze_before_trial": True, "same_inputs": True,
            "same_environment": True, "same_time_budget": True,
            "repeat_when_noisy": True},
        "trial": {"change": "one_named_dimension",
                  "editable_surface": "smallest_figma_skill_owner",
                  "ledger_statuses": ["keep", "discard", "crash"]},
        "resource_policy": "measure_or_justify_not_applicable",
        "resource_catalog": {name: ["measured_value"] for name in RESOURCES},
        "protected_dimensions": PROTECTED,
        "acceptance": "pareto_non_regression",
        "failure": "restore_last_accepted_version",
        "required_evidence": EVIDENCE}
