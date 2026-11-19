"""Tasks on one day form a single block."""

import pyomo.environ as pyo


class NoIntradayGap:
    """A person works at most one contiguous block of tasks per day.

    A block starts on a worked task that does not begin when the previous
    offered task ends. A clock gap counts even when no task fills it.
    """

    @staticmethod
    def add(model, instance) -> None:
        """Attach the rule to ``model``."""

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
