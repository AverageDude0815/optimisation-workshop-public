"""Target time. ``target**2 - (hours - target)**2`` for each person."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyomo.environ as pyo

if TYPE_CHECKING:
    from workshop.model import Instance


class TargetTime:
    """``target**2 - (hours - target)**2`` summed over the people.

    The square is linear between the hour totals one person can actually
    produce, so every feasible roster gets the exact square. Each person peaks
    at ``target**2`` when their hours land on the target.
    """

    @staticmethod
    def reward(instance: Instance, assignments: tuple[tuple[str, str, str], ...]) -> float:
        """Score one roster that is already chosen, without solving.

        Each person contributes ``target_hours**2 - (hours - target_hours)**2``.
        That contribution peaks at ``target_hours**2`` when their hours land
        on the target, and it is 0 when they miss by the whole target.

        Args:
            instance: The fixed roster. ``persons`` is who is scored,
                ``target_hours`` is the peak, and each task's ``hours`` comes
                from ``shifts``.
            assignments: Chosen tuples ``(person, day, shift_name)``.

        Returns:
            The sum of the per-person rewards.
        """

        hours_of = {shift.name: shift.hours for shift in instance.shifts}
        totals = {person: 0.0 for person in instance.persons}
        for person, _day, shift in assignments:
            totals[person] += hours_of[shift]
        target = instance.target_hours
        return sum(target * target - (totals[person] - target) ** 2 for person in instance.persons)

    @staticmethod
    def gap_breakpoints(instance: Instance, target_hours: float) -> list[float]:
        """Absolute hour gaps of every total one person can produce.

        Pyomo cannot put a square into a linear model directly. The square is
        drawn as straight segments between these gaps, and the segments pass
        through ``gap**2``, so every total someone can actually work is exact.

        Args:
            instance: The fixed roster. The possible totals are sums of
                ``hours`` from ``shifts_on`` across the days.
            target_hours: The hour total a person is aiming for. A gap of 0
                means they landed on it.

        Returns:
            The gaps, sorted, including 0.
        """

        totals = {0.0}
        for day in instance.days:
            for shift in instance.shifts_on(day):
                totals = {total + shift.hours for total in totals} | totals
        gaps = {abs(total - target_hours) for total in totals}
        gaps.add(0.0)
        return sorted(gaps)

    @staticmethod
    def add(model: pyo.ConcreteModel, instance: Instance, target_hours: float) -> None:
        """Attach the target-time score to ``model``.

        Each person's hours are the sum of the lengths of the tasks they
        work. The reward is ``target_hours**2 - (hours - target_hours)**2``.

        Args:
            model: The Pyomo problem. Hours are built from
                ``model.x[person, day, shift_name]``, which is 1 when that
                task is worked. The sum of the rewards is stored on
                ``model.target_score``.
            instance: The fixed roster. ``persons``, ``days``, and
                ``shifts_on(day)`` say which tasks can contribute hours.
                ``Shift.hours`` is the length of one task.
            target_hours: The hour total where one person's reward peaks.
                Pass 42 in this workshop. ``instance.target_hours`` is that
                same number.

        Returns:
            None. ``model`` gains ``target_score``.
        """

        persons = instance.persons
        days = instance.days
        hours = {
            person: sum(
                model.x[person, day, shift.name] * shift.hours
                for day in days
                for shift in instance.shifts_on(day)
            )
            for person in persons
        }
        breakpoints = TargetTime.gap_breakpoints(instance, target_hours)
        model.absolute_gap = pyo.Var(
            persons, domain=pyo.NonNegativeReals, bounds=(0, breakpoints[-1])
        )
        model.squared_gap = pyo.Var(
            persons, domain=pyo.NonNegativeReals, bounds=(0, breakpoints[-1] ** 2)
        )
        for person in persons:
            gap = hours[person] - target_hours
            model.rules.add(model.absolute_gap[person] >= gap)
            model.rules.add(model.absolute_gap[person] >= -gap)
        model.square = pyo.Piecewise(
            persons,
            model.squared_gap,
            model.absolute_gap,
            pw_pts=breakpoints,
            pw_repn="INC",
            f_rule=lambda _model, _person, point: point**2,
            pw_constr_type="LB",
            unbounded_domain_var=True,
        )
        model.hours = pyo.Expression(expr=sum(hours.values()))
        model.target_score = pyo.Expression(
            expr=sum(target_hours**2 - model.squared_gap[person] for person in persons)
        )
