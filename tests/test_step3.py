"""Step 3. Raw weights should keep consistency above 95% and target time above 75%."""

from workshop.black_box_model.optimize import solve_objective
from workshop.model import WORKSHOP
from workshop.steps.step3 import objective_weights

from balanced_roster import assert_consistency_above_95_and_target_above_75, model_with_rule


def solve():
    consistency_weight, target_weight = objective_weights()
    return solve_objective(
        WORKSHOP,
        model_with_rule(),
        lambda built: (
            consistency_weight * built.consistency_score + target_weight * built.target_score
        ),
    )


def test_consistency_stays_above_95_and_target_above_75():
    assert_consistency_above_95_and_target_above_75(solve())
