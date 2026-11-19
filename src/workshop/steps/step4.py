"""Step 4. An analytical normaliser makes the weights easier to tune.

Divide each score by its maximum reward. Run this step once with both weights
at 1: the two objectives are then on the same scale, so neither one dominates.
Then change the weights so consistent schedule is above 95% of its maximum and
target time stays above 75%.
"""

from workshop.model import Instance


def objective_weights() -> tuple[float, float]:
    """Implement step 4. Change the weights on the normalised scores.

    Each score is divided by the maximum you return from the two functions
    below, and only then multiplied by these weights. A weight of 1 means
    one full share of that objective. Run once with both weights at 1 and
    read the two percentages before you change them.

    There are no arguments. Edit the two numbers in the marked block.

    Returns:
        ``(consistency_weight, target_time_weight)``. If consistent schedule
        stays under 95%, raise only that weight. If target time falls
        through 75%, bring it back down.
    """

    ### CHANGE VALUES HERE ###
    consistency_weight = 1.0
    target_time_weight = 1.0
    return consistency_weight, target_time_weight
    ### END CHANGE HERE ###


def normalize_consistent_schedule(instance: Instance) -> float:
    """Implement step 4. Analytical normalisation for consistent schedule.

    Return the highest this score can be, from its formula, before any
    roster is solved. The solver later divides the score by this number.
    Each term in the score is worth at most 1.

    Args:
        instance: The fixed roster. Fields that describe this score:

            ``persons``
                One set of terms is kept for each person.
            ``pairs``
                Consecutive days, each entry ``(today, tomorrow)``. The
                week does not wrap.
            ``shared_shifts(today, tomorrow)``
                Tasks offered on both days of that pair. Only those starts
                are terms. A matching start is worth at most 1.
            ``shifts``
                Every distinct task in the week, including starts that are
                never offered on two consecutive days. Those starts are not
                terms.

    Returns:
        The maximum reward of ``consistency_score``.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###


def normalize_target_time(instance: Instance) -> float:
    """Implement step 4. Analytical normalisation for target time.

    Return the highest this score can be, from its formula, before any
    roster is solved. A real roster may be unable to land on that peak.
    Use the peak of the formula anyway.

    One person's reward is ``target_hours**2 - (hours - target_hours)**2``.
    It peaks when that person's hours equal ``target_hours``.

    Args:
        instance: The fixed roster. Useful fields:

            ``persons``
                Each person has their own hour total and their own peak.
            ``target_hours``
                The hour total where one person's reward peaks. This
                workshop uses 42.

    Returns:
        The maximum reward of ``target_score``.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
