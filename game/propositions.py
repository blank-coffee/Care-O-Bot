#
# Shared proposition vocabulary
#
# Every game component should import from here.
#

VALID_PROPOSITIONS = [
    "task_active",
    "navigation_active",
    "waiting_for_human",
    "task_completed",
    "object_carried",
    "low_battery",
    "recovery_active",
    "human_near",
    "safety_stop",

    # optional extras from model
    "delivered",
    "in_error",
    "charging"
]


LTL_OPERATORS = [
    "[]",
    "<>",
    "!",
    "&",
    "|",
    "->",
    "U"
]