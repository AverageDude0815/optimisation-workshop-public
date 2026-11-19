"""Step 2. Objectives can conflict, and the larger reward wins.

Keep step 1 and forbid a gap inside the day. Run step 1, then run this step,
and compare the rosters. Target time wants the 8-hour block, which is
08:00–16:00 on a Monday-type day and 00:00–08:00 on a Tuesday-type day.
Consistent schedule wants 00:00 or 12:00 every day. The plain sum follows
target time, because that reward is much larger.
"""

import pyomo.environ as pyo

from workshop.constraint.no_intraday_gap import NoIntradayGap
from workshop.model import Instance
from workshop.steps import step1


def build_model(model: pyo.ConcreteModel, instance: Instance) -> None:
    """Implement step 2. Keep step 1, and add the no-gap rule.

    ``model`` and ``instance`` are the same objects as in step 1. Step 1 has
    already attached both scores and the three rules. Add the class that
    forbids a gap inside a single day. Its ``add`` takes ``model`` and
    ``instance`` and needs no extra number.

    A gap is on the clock, not in the list of offered tasks. Two tasks touch
    only when the earlier one's ``end_hour`` equals the later one's
    ``start_hour``. On a Monday-type day the only 8-hour block is 08:00–16:00.
    On a Tuesday-type day it is 00:00–08:00. Target time wants that block.
    Consistent schedule wants 00:00 or 12:00 every day, and the block does
    not repeat that start.

    Run step 1, then run this step, and compare the rosters.

    Args:
        model: The Pyomo problem, already containing step 1.
        instance: The fixed roster. ``shifts_on(day)`` is that day's tasks,
            and each ``Shift`` has ``start_hour`` and ``end_hour``.

    Returns:
        None. ``model`` also gains the no-gap rule.
    """

    step1.build_model(model, instance)
    ### ADD CODE HERE ###
    ### END CODE HERE ###
