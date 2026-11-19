"""Target time. ``target**2 - (hours - target)**2`` for each person."""

import pyomo.environ as pyo


class TargetTime:
    """``target**2 - (hours - target)**2`` summed over the people.

    The square is linear between the hour totals one person can actually
    produce, so every feasible roster gets the exact square. Each person peaks
    at ``target**2`` when their hours land on the target.
    """

    @staticmethod
    def reward(instance, assignments: tuple[tuple[str, str, str], ...]) -> float:
        """Sum of ``target**2 - (hours - target)**2`` over the people."""

        hours_of = {shift.name: shift.hours for shift in instance.shifts}
        totals = {person: 0.0 for person in instance.persons}
        for person, _day, shift in assignments:
            totals[person] += hours_of[shift]
        target = instance.target_hours
        return sum(target * target - (totals[person] - target) ** 2 for person in instance.persons)

    @staticmethod
    def gap_breakpoints(instance, target_hours: float) -> list[float]:
        """Absolute hour gaps of every total one person can produce.

        The piecewise square equals ``gap**2`` at each of these points.
        """

        totals = {0.0}
        for day in instance.days:
            for shift in instance.shifts_on(day):
                totals = {total + shift.hours for total in totals} | totals
        gaps = {abs(total - target_hours) for total in totals}
        gaps.add(0.0)
        return sorted(gaps)

    @staticmethod
    def add(model, instance, target_hours: float) -> None:
        """Attach the score to ``model`` for this per-person hour target."""

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
