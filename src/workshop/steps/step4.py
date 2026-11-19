"""Step 4. An analytical normaliser makes the weights easier to tune.

Divide each score by its maximum reward. Run this step once with both weights
at 1: the two objectives are then on the same scale, so neither one dominates.
Then change the weights so consistent schedule is above 95% of its maximum and
target time stays above 75%.
"""


def objective_weights() -> tuple[float, float]:
    """Implement step 4. Change the weights on the normalised scores.

    Returns:
        The consistency weight and the target-time weight.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###


def normalize_consistent_schedule(instance) -> float:
    """Implement step 4. Analytical normalisation for consistent schedule.

    Returns:
        The maximum reward of ``consistency_score``.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###


def normalize_target_time(instance) -> float:
    """Implement step 4. Analytical normalisation for target time.

    Returns:
        The maximum reward of ``target_score``.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
