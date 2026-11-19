"""Step 3. Weighting is hard when the objectives are not normalised.

The raw rewards have very different sizes, so a sensible weight is hard to
guess. Change the two weights, before either score is scaled, so consistent
schedule is above 95% of its maximum reward and target time stays above 75%.
"""


def objective_weights() -> tuple[float, float]:
    """Implement step 3. Change the raw weights, before either score is scaled.

    The solver maximises ``consistency_weight * consistency_score +
    target_time_weight * target_score``. Neither score is divided by its
    maximum first, so the two numbers in the product have very different
    sizes. The weights have to make up for that.

    There are no arguments. Edit the two numbers in the marked block.

    Returns:
        ``(consistency_weight, target_time_weight)``. Raise the consistency
        weight when that score is being ignored. If target time falls through
        75% of its maximum, that weight went too far. Stop above 95%
        consistency and above 75% target time.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###
