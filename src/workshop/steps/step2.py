"""Step 2. Objectives can conflict, and the larger reward wins.

Keep step 1 and forbid a gap inside the day. Run step 1, then run this step,
and compare the rosters. Target time wants the 8-hour block, which is
08:00–16:00 on a Monday-type day and 00:00–08:00 on a Tuesday-type day.
Consistent schedule wants 00:00 or 12:00 every day. The plain sum follows
target time, because that reward is much larger.
"""

from workshop.constraint.no_intraday_gap import NoIntradayGap
from workshop.steps import step1


def build_model(model, instance) -> None:
    """Implement step 2. Keep step 1, and add the no-gap rule.

    Tasks on one day must form one block. On a Monday-type day the only 8-hour
    block is 08:00–16:00. On a Tuesday-type day it is 00:00–08:00. Target time
    wants that block. Consistent schedule wants 00:00 or 12:00 every day, and
    the block does not repeat that start.

    Run step 1, then run this step, and compare the rosters.

    Returns:
        None. ``model`` also gains the no-gap rule.
    """

    step1.build_model(model, instance)
    ### ADD CODE HERE ###
    ### END CODE HERE ###
