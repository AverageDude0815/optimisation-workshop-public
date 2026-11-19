"""Step 1. Building a model is easy while the objectives do not conflict.

Add one score or rule at a time, and run this step after each addition. Look at
how the roster changes. The scores are consistent schedule and target time,
which needs 42 hours for each person. The rules are at most 8 hours on a day,
two days off in a row, and only one person on a task. A day may still contain
a gap.
"""

from workshop.constraint.consecutive_days_off import ConsecutiveDaysOff
from workshop.constraint.max_hours_per_day import MaxHoursPerDay
from workshop.constraint.one_person_per_task import OnePersonPerTask
from workshop.objective.consistent_schedule import ConsistentSchedule
from workshop.objective.target_time import TargetTime


def build_model(model, instance) -> None:
    """Implement step 1. Add consistent schedule, target time, and three rules.

    Add these:

    - Consistent schedule.
    - Target time. It needs 42 hours for each person.
    - At most 8 hours for each person on a day.
    - Two days off in a row for each person.
    - Only one person can work a task.

    A day may still contain a gap. Add these one at a time. After each one, run
    this step and look at how the roster changes.

    Returns:
        None. ``model`` gains ``consistency_score``, ``target_score``, and the three rules.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
