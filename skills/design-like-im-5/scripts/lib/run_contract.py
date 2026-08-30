"""Set fixed run rules."""

NEEDED = [
    "outcome", "audience", "platform", "primary_tasks",
    "source_permissions", "proof_threshold",
]
MODEL_ACTIONS = [
    "source_meaning", "state_judgment", "atom_judgment", "part_design",
    "screen_design", "motion_judgment", "visual_review", "plain_readback",
]
NEXT_AFTER_RECORD = {
    "source_meaning": "state_judgment",
    "state_judgment": "select_rules",
    "atom_judgment": "part_design",
    "part_design": "screen_design",
    "screen_design": "motion_judgment",
    "motion_judgment": "visual_review",
    "visual_review": "plain_readback",
    "plain_readback": "check_lineage",
}
