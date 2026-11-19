"""Read a solved roster and check it against the closed-form scores."""

import pyomo.environ as pyo

from workshop.model import Instance, RosterScore, slots
from workshop.objective.consistent_schedule import ConsistentSchedule
from workshop.objective.target_time import TargetTime

TOL = 1e-5


def roster_hours(instance: Instance, assignments: tuple[tuple[str, str, str], ...]) -> float:
    hours_of = {shift.name: shift.hours for shift in instance.shifts}
    return sum(hours_of[shift] for _person, _day, shift in assignments)


def read_roster(instance: Instance, model: pyo.ConcreteModel) -> RosterScore:
    """Read one solved model. Both scores are meaningful when the plain sum built it."""

    assignments = tuple(
        (person, day, shift)
        for person, day, shift in slots(instance)
        if pyo.value(model.x[person, day, shift]) > 0.5
    )
    scored = RosterScore(
        assignments=assignments,
        hours=float(pyo.value(model.hours)),
        consistency=float(pyo.value(model.consistency_score)),
        target=float(pyo.value(model.target_score)),
    )
    if abs(scored.hours - roster_hours(instance, assignments)) > TOL:
        raise RuntimeError("solved hours do not match the assigned shifts")
    if abs(scored.consistency - ConsistentSchedule.points(instance, assignments)) > TOL:
        raise RuntimeError("solved consistency does not match the schedule rule")
    expected_target = TargetTime.reward(instance, assignments)
    if abs(scored.target - expected_target) > 1e-4:
        raise RuntimeError(
            "solved target time does not match target**2 - (hours - target)**2: "
            f"solver {scored.target}, formula {expected_target}"
        )
    return scored
