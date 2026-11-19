"""Step 5. An LP maximum gives the same balance without an analytical one.

Dividing by the LP maximum reaches the same kind of roster as step 4. The
difference is that a new objective no longer needs the engineering effort of
finding its maximum by hand. Change the weights so consistent schedule is above
95% of its maximum reward and target time stays above 75%.
"""

import pyomo.environ as pyo

from workshop.lp import lp_maximum


def objective_weights() -> tuple[float, float]:
    """Implement step 5. Change the weights on the LP-normalised scores.

    Same role as step 4. Each score is divided by the maximum from
    ``lp_divisors``, then multiplied by these weights. Start with both
    weights at 1.

    There are no arguments. Edit the two numbers in the marked block.

    Returns:
        ``(consistency_weight, target_time_weight)``. Stop when consistent
        schedule is above 95% and target time is still above 75%.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###


def lp_divisors(model: pyo.ConcreteModel) -> tuple[float, float]:
    """Implement step 5. LP normalisation for both objectives.

    Normally ``model.x`` is 0 or 1: a task is assigned or it is not. For
    this function those decisions are already relaxed, so a person may be
    given a fraction of a task. That is a linear program. It is not a roster
    anyone can work. It is how you ask for the largest one score can be
    without deriving that peak by hand.

    ``lp_maximum(model, expression)`` maximises a single expression and
    returns that maximum as a number. Call it once per score.

    Args:
        model: The relaxed Pyomo problem. ``model.consistency_score`` is the
            consistent-schedule expression. ``model.target_score`` is the
            target-time expression. Both are already attached. Pass each one
            to ``lp_maximum`` on its own, not the sum of the two.

    Returns:
        The maximum reward of consistency and the maximum reward of target time.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
