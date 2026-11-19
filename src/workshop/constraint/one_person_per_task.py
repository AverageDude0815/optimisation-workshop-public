"""A task has at most one person."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class OnePersonPerTask:
    """Each offered task is assigned to at most one person."""

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance) -> None:
        """Attach the one-person rule to ``model``.

        A task may be left uncovered. It may not be given to two people.
        Nothing in the model requires every task to be staffed.

        Args:
            model: The Pyomo problem. ``model.x[person, day, shift_name]`` is
                1 when that person works that task. The rule is added to
                ``model.rules``.
            instance: The fixed roster. ``days`` and ``shifts_on(day)`` list
                the tasks. ``persons`` is everyone who might be assigned one.
        """

        for day in instance.days:
            for shift in instance.shifts_on(day):
                assigned = sum(model.x[person, day, shift.name] for person in instance.persons)
                model.rules.add(assigned <= 1)
