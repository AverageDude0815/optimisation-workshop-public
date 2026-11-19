"""A cap on hours worked in one day."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class MaxHoursPerDay:
    """Each person stays within ``max_hours`` on every day."""

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance, max_hours: float) -> None:
        """Attach the daily hour cap to ``model``.

        Args:
            model: The Pyomo problem. ``model.x[person, day, shift_name]`` is
                1 when that person works that task. The cap is added to
                ``model.rules``. This method does not solve.
            instance: The fixed roster. ``persons`` and ``days`` are the
                loops. ``shifts_on(day)`` is that day's tasks, and each
                task's ``hours`` is its length.
            max_hours: The most one person may work on one day. Pass 8 in
                this workshop, which is two of the 4-hour tasks.
        """

        for person in instance.persons:
            for day in instance.days:
                worked = sum(
                    model.x[person, day, shift.name] * shift.hours
                    for shift in instance.shifts_on(day)
                )
                model.rules.add(worked <= max_hours)
