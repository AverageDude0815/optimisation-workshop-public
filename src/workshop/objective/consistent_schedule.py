"""Consistent schedule. One point when a start time matches on consecutive days."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class ConsistentSchedule:
    """One point per person and shift when the worked state matches on consecutive days.

    The same start on the next day scores 1 when both days are worked or both
    are off, and 0 on a mismatch.
    """

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance) -> None:
        """Attach the consistent-schedule score to ``model``.

        One term is worth 1 when the same start is in the same state on both
        days of a consecutive pair: both worked, or both off. A mismatch is
        worth 0. Starts that are not offered on both days are not terms.

        Args:
            model: The Pyomo problem. ``model.x[person, day, shift_name]`` is
                the 0-or-1 decision for that assignment. This method does not
                read those values. It adds symbols the solver will fill in,
                and stores their sum on ``model.consistency_score``.
            instance: The fixed roster. The terms come from ``persons``,
                ``pairs``, and ``shared_shifts(today, tomorrow)``.

        Returns:
            None. ``model`` gains ``consistency_score``.
        """

        terms = [
            (person, today, tomorrow, shift.name)
            for person in instance.persons
            for today, tomorrow in instance.pairs
            for shift in instance.shared_shifts(today, tomorrow)
        ]
        model.consistent = pyo.Var(terms, domain=pyo.NonNegativeReals)
        for person, today, tomorrow, shift in terms:
            worked_today = model.x[person, today, shift]
            worked_tomorrow = model.x[person, tomorrow, shift]
            consistency = model.consistent[person, today, tomorrow, shift]
            model.rules.add(consistency <= 1 - (worked_today - worked_tomorrow))
            model.rules.add(consistency <= 1 - (worked_tomorrow - worked_today))
        model.consistency_score = pyo.Expression(
            expr=sum(model.consistent[term] for term in terms)
        )

    @staticmethod
    def points(instance: Instance, assignments: tuple[tuple[str, str, str], ...]) -> float:
        """Score one roster that is already chosen, without solving.

        Args:
            instance: The fixed roster. Same terms as ``add``: one per person,
                consecutive pair, and shared start.
            assignments: Chosen tuples ``(person, day, shift_name)``.

        Returns:
            How many of those terms match. Each match is worth 1.
        """

        assigned = set(assignments)
        score = 0.0
        for person in instance.persons:
            for today, tomorrow in instance.pairs:
                for shift in instance.shared_shifts(today, tomorrow):
                    worked_today = (person, today, shift.name) in assigned
                    worked_tomorrow = (person, tomorrow, shift.name) in assigned
                    if worked_today == worked_tomorrow:
                        score += 1.0
        return score
