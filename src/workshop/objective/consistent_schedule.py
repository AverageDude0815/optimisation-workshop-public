"""Consistent schedule. One point when a start time matches on consecutive days."""

import pyomo.environ as pyo


class ConsistentSchedule:
    """One point per person and shift when the worked state matches on consecutive days.

    The same start on the next day scores 1 when both days are worked or both
    are off, and 0 on a mismatch.
    """

    @staticmethod
    def add(model, instance) -> None:
        """Attach the score to ``model``."""

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
    def points(instance, assignments: tuple[tuple[str, str, str], ...]) -> float:
        """Closed-form score for one fixed roster."""

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
