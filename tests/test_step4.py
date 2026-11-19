"""Step 4. Normalised scores stay above 90% at equal weights, and the chosen weights clear 95% and 75%."""

from workshop.black_box_model.optimize import solve_objective
from workshop.model import WORKSHOP
from workshop.steps.step4 import (
    normalize_consistent_schedule,
    normalize_target_time,
    objective_weights,
)

from balanced_roster import (
    assert_both_objectives_above_90,
    assert_consistency_above_95_and_target_above_75,
    model_with_rule,
)


def solve(consistency_weight, target_weight):
    consistency_divisor = normalize_consistent_schedule(WORKSHOP)
    target_divisor = normalize_target_time(WORKSHOP)
    return solve_objective(
        WORKSHOP,
        model_with_rule(),
        lambda built: (
            consistency_weight * built.consistency_score / consistency_divisor
            + target_weight * built.target_score / target_divisor
        ),
    )


def test_step4_norm():
    assert_both_objectives_above_90(solve(1.0, 1.0))


def test_step_4_weights():
    consistency_weight, target_weight = objective_weights()
    assert_consistency_above_95_and_target_above_75(solve(consistency_weight, target_weight))
