"""Step 1. Building a model is easy while the objectives do not conflict.

Add one score or rule at a time, and run this step after each addition. Look at
how the roster changes. The scores are consistent schedule and target time,
which needs 42 hours for each person. The rules are at most 8 hours on a day,
two days off in a row, and only one person on a task. A day may still contain
a gap.
"""

import pyomo.environ as pyo

from workshop.constraint.consecutive_days_off import ConsecutiveDaysOff
from workshop.constraint.max_hours_per_day import MaxHoursPerDay
from workshop.constraint.one_person_per_task import OnePersonPerTask
from workshop.model import Instance
from workshop.objective.consistent_schedule import ConsistentSchedule
from workshop.objective.target_time import TargetTime


def build_model(model: pyo.ConcreteModel, instance: Instance) -> None:
    """Implement step 1. Add consistent schedule, target time, and three rules.

    Pyomo is the library that searches for the best roster. A
    ``ConcreteModel`` is one concrete problem: decisions, rules, and a score
    to make as large as possible. This function does not solve. It attaches
    the scores and the rules. Each class below has an ``add`` method. Call
    it with ``model`` and ``instance``.

    ``model.x[person, day, shift_name]`` will be 1 if that person works that
    task on that day, and 0 otherwise. The solver chooses those values later.
    While you are building the model, ``x`` is a symbol, not a Python number.
    Pass ``model`` into ``add`` and let that method use it.

    ``instance`` is ordinary data you can read now. The fields you need are
    on ``Instance``: ``persons``, ``days``, ``shifts_on(day)``, and
    ``target_hours`` (42). You do not have to read them yourself in this
    step. The ``add`` methods read them.

    Add these one at a time. After each one, run this step and look at how
    the roster changes.

    - Consistent schedule.
    - Target time. It needs 42 hours for each person.
    - At most 8 hours for each person on a day.
    - Two days off in a row for each person.
    - Only one person can work a task.

    A day may still contain a gap.

    Args:
        model: The Pyomo problem. It already has ``x`` and an empty
            ``rules`` list. Each ``add`` hangs a score or a rule on it.
        instance: The fixed roster: who, which days, which tasks, and the
            42-hour target.

    Returns:
        None. ``model`` gains ``consistency_score``, ``target_score``, and the three rules.
    """

    ### ADD CODE HERE ###
    ### END CODE HERE ###
