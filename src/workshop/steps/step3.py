"""Step 3. Weighting is hard when the objectives are not normalised.

The raw rewards have very different sizes, so a sensible weight is hard to
guess. Change the two weights, before either score is scaled, so consistent
schedule is above 95% of its maximum reward and target time stays above 75%.
"""


def objective_weights() -> tuple[float, float]:
    """Implement step 3. Change the raw weights, before either score is scaled.

    Returns:
        The consistency weight and the target-time weight.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###
