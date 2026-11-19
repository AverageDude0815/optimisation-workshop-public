"""Tasks on one day form a single block."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class NoIntradayGap:
    """A person works at most one contiguous block of tasks per day.

    A block starts on a worked task that does not begin when the previous
    offered task ends. A clock gap counts even when no task fills it.
    """

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance) -> None:
        """Attach the no-gap rule to ``model``.

        On one day, the tasks one person works must form a single block on
        the clock. Monday 00:00–04:00 together with 08:00–12:00 is a gap,
        even though 04:00–08:00 is not offered that day. The previous task
        abuts this one only when its ``end_hour`` equals this task's
        ``start_hour``.

        Args:
            model: The Pyomo problem. ``model.x[person, day, shift_name]`` is
                1 when that person works that task. The rule is added to
                ``model.rules``.
            instance: The fixed roster. ``persons``, ``days``, and
                ``shifts_on(day)`` give the tasks in start-time order.
                ``Shift.start_hour`` and ``Shift.end_hour`` decide whether
                two tasks touch.
        """

        index = [
            (person, day, shift.name)
            for person in instance.persons
            for day in instance.days
            for shift in instance.shifts_on(day)
        ]
        model.block_start = pyo.Var(index, domain=pyo.Binary)
        for person in instance.persons:
            for day in instance.days:
                ordered = instance.shifts_on(day)
                for position, shift in enumerate(ordered):
                    worked = model.x[person, day, shift.name]
                    start = model.block_start[person, day, shift.name]
                    model.rules.add(start <= worked)
                    abuts = position > 0 and ordered[position - 1].end_hour == shift.start_hour
                    if abuts:
                        previous = model.x[person, day, ordered[position - 1].name]
                        model.rules.add(start >= worked - previous)
                    else:
                        model.rules.add(start >= worked)
                model.rules.add(
                    sum(model.block_start[person, day, shift.name] for shift in ordered) <= 1
                )
