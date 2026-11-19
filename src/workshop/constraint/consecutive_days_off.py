"""At least one run of days off inside the week."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class ConsecutiveDaysOff:
    """Each person has one run of fully off days.

    A day is off when none of its shifts is assigned. The run is consecutive
    days inside the week, and the week does not wrap from Sunday back to Monday.
    """

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance, days_in_a_row: int) -> None:
        """Attach the days-off rule to ``model``.

        Each person needs one run of fully off days. A day is off when none
        of its tasks is worked. The run sits inside the week: Sunday and
        Monday are not a run, because the week does not wrap.

        Args:
            model: The Pyomo problem. ``model.x[person, day, shift_name]`` is
                1 when that person works that task. The rule is added to
                ``model.rules``.
            instance: The fixed roster. ``persons``, ``days``, and
                ``shifts_on(day)`` say what "working a day" means.
            days_in_a_row: How long the off run must be. Pass 2 in this
                workshop.
        """

        if days_in_a_row < 2:
            raise ValueError("a days-off run needs at least two days")
        days = instance.days
        if days_in_a_row > len(days):
            raise ValueError("the week is shorter than the required days off")
        starts = list(range(len(days) - days_in_a_row + 1))
        model.day_off = pyo.Var(instance.persons, days, domain=pyo.Binary)
        model.off_run = pyo.Var(instance.persons, starts, domain=pyo.Binary)
        for person in instance.persons:
            for day in days:
                assigned = [model.x[person, day, shift.name] for shift in instance.shifts_on(day)]
                for assignment in assigned:
                    model.rules.add(model.day_off[person, day] <= 1 - assignment)
                model.rules.add(model.day_off[person, day] >= 1 - sum(assigned))
            for start in starts:
                window = days[start : start + days_in_a_row]
                run = model.off_run[person, start]
                for day in window:
                    model.rules.add(run <= model.day_off[person, day])
                model.rules.add(
                    run >= sum(model.day_off[person, day] for day in window) - (days_in_a_row - 1)
                )
            model.rules.add(sum(model.off_run[person, start] for start in starts) >= 1)
