"""Step 5. An LP maximum gives the same balance without an analytical one.

Dividing by the LP maximum reaches the same kind of roster as step 4. The
difference is that a new objective no longer needs the engineering effort of
finding its maximum by hand. Change the weights so consistent schedule is above
95% of its maximum reward and target time stays above 75%.
"""

from workshop.lp import lp_maximum


def objective_weights() -> tuple[float, float]:
    """Implement step 5. Change the weights on the LP-normalised scores.

    Returns:
        The consistency weight and the target-time weight.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###


def lp_divisors(model) -> tuple[float, float]:
    """Implement step 5. LP normalisation for both objectives.

    The discrete variables are already relaxed. Take one LP maximum per score.

    Returns:
        The maximum reward of consistency and the maximum reward of target time.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
