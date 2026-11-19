"""Step 5. LP-normalised scores stay above 90% at equal weights, and the chosen weights clear 95% and 75%."""

import pytest

from workshop.lp import (
    relax_discrete_variables,
    require_continuous,
    restore_discrete_variables,
)
from workshop.black_box_model.optimize import solve_objective
from workshop.model import WORKSHOP
from workshop.steps.step5 import lp_divisors, objective_weights

from balanced_roster import (
    assert_both_objectives_above_90,
    assert_consistency_above_95_and_target_above_75,
    model_with_rule,
)


@pytest.fixture(scope="module")
def divisors():
    reference = model_with_rule()
    relaxed = relax_discrete_variables(reference)
    try:
        require_continuous(reference)
        return lp_divisors(reference)
    finally:
        restore_discrete_variables(relaxed)


def solve(divisors, consistency_weight, target_weight):
    consistency_divisor, target_divisor = divisors
    return solve_objective(
        WORKSHOP,
        model_with_rule(),
        lambda built: (
            consistency_weight * built.consistency_score / consistency_divisor
            + target_weight * built.target_score / target_divisor
        ),
    )


def test_step5_norm(divisors):
    assert_both_objectives_above_90(solve(divisors, 1.0, 1.0))


def test_step_5_weights(divisors):
    consistency_weight, target_weight = objective_weights()
    assert_consistency_above_95_and_target_above_75(
        solve(divisors, consistency_weight, target_weight)
    )
