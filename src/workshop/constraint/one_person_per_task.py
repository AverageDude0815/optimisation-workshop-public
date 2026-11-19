"""A task has at most one person."""


class OnePersonPerTask:
    """Each offered task is assigned to at most one person."""

    @staticmethod
    def add(model, instance) -> None:
        """Attach the rule to ``model``."""

        for day in instance.days:
            for shift in instance.shifts_on(day):
                assigned = sum(model.x[person, day, shift.name] for person in instance.persons)
                model.rules.add(assigned <= 1)
