"""A cap on hours worked in one day."""

class MaxHoursPerDay:
    """Each person stays within ``max_hours`` on every day."""

    @staticmethod
    def add(model, instance, max_hours: float) -> None:
        """Attach the rule to ``model``."""

        for person in instance.persons:
            for day in instance.days:
                worked = sum(
                    model.x[person, day, shift.name] * shift.hours
                    for shift in instance.shifts_on(day)
                )
                model.rules.add(worked <= max_hours)
