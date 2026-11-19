"""The roster instance and its assignment variables."""

from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo

from workshop.objective.consistent_schedule import ConsistentSchedule
from workshop.objective.target_time import TargetTime


@dataclass(frozen=True)
class Shift:
    """One task: a start time and a length."""

    name: str
    start_hour: int
    hours: float

    @property
    def end_hour(self) -> int:
        return self.start_hour + int(self.hours)


@dataclass(frozen=True)
class Instance:
    """A week of tasks for each person, and one hour target per person.

    ``shifts_by_day`` lines up with ``days``. A task is offered only on the
    days that list it.
    """

    days: tuple[str, ...]
    persons: tuple[str, ...]
    shifts_by_day: tuple[tuple[Shift, ...], ...]
    target_hours: float

    def __post_init__(self) -> None:
        if len(self.persons) < 1:
            raise ValueError("need at least one person")
        if len(self.days) < 2:
            raise ValueError("consistency needs two consecutive days")
        if len(self.shifts_by_day) != len(self.days):
            raise ValueError("each day needs its own tasks")
        if self.target_hours <= 0:
            raise ValueError("target hours must be positive")
        known: dict[str, Shift] = {}
        for day, day_shifts in zip(self.days, self.shifts_by_day):
            if len(day_shifts) < 1:
                raise ValueError(f"{day} needs at least one task")
            ordered = sorted(day_shifts, key=lambda shift: shift.start_hour)
            starts = [shift.start_hour for shift in ordered]
            if len(starts) != len(set(starts)):
                raise ValueError(f"{day} repeats a start time")
            for earlier, later in zip(ordered, ordered[1:]):
                if earlier.end_hour > later.start_hour:
                    raise ValueError(f"{day}: {earlier.name} overlaps {later.name}")
            for shift in day_shifts:
                previous = known.get(shift.name)
                if previous is not None and (
                    previous.start_hour != shift.start_hour or previous.hours != shift.hours
                ):
                    raise ValueError(f"{shift.name} changes between days")
                known[shift.name] = shift

    def shifts_on(self, day: str) -> tuple[Shift, ...]:
        """Tasks offered on ``day``, in start-time order."""

        ordered = sorted(
            self.shifts_by_day[self.days.index(day)], key=lambda shift: shift.start_hour
        )
        return tuple(ordered)

    def shared_shifts(self, today: str, tomorrow: str) -> tuple[Shift, ...]:
        """Tasks offered on both days. Consistency compares these starts."""

        tomorrow_names = {shift.name for shift in self.shifts_on(tomorrow)}
        return tuple(shift for shift in self.shifts_on(today) if shift.name in tomorrow_names)

    @property
    def shifts(self) -> tuple[Shift, ...]:
        """Every distinct task, ordered by start time."""

        by_name: dict[str, Shift] = {}
        for day_shifts in self.shifts_by_day:
            for shift in day_shifts:
                by_name.setdefault(shift.name, shift)
        return tuple(sorted(by_name.values(), key=lambda shift: shift.start_hour))

    @property
    def pairs(self) -> tuple[tuple[str, str], ...]:
        """Consecutive days. Each entry is ``(today, tomorrow)``."""

        return tuple(
            (self.days[index], self.days[index + 1]) for index in range(len(self.days) - 1)
        )


@dataclass(frozen=True)
class RosterScore:
    """Solver values for one assignment."""

    assignments: tuple[tuple[str, str], ...]
    hours: float
    consistency: float
    target: float

    @property
    def plain_sum(self) -> float:
        return self.consistency + self.target

    def weighted(self, target_weight: float) -> float:
        return self.consistency + target_weight * self.target


# Monday-type days offer 00:00–04:00, 08:00–12:00, and 12:00–16:00.
# Tuesday-type days offer 00:00–04:00, 04:00–08:00, and 12:00–16:00.
# The two lists alternate, starting on Monday.
_MONDAY_TASKS = (
    Shift("00:00", start_hour=0, hours=4),
    Shift("08:00", start_hour=8, hours=4),
    Shift("12:00", start_hour=12, hours=4),
)
_TUESDAY_TASKS = (
    Shift("00:00", start_hour=0, hours=4),
    Shift("04:00", start_hour=4, hours=4),
    Shift("12:00", start_hour=12, hours=4),
)
_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
WORKSHOP = Instance(
    days=_DAYS,
    persons=("Alex", "Sam"),
    shifts_by_day=tuple(
        _MONDAY_TASKS if index % 2 == 0 else _TUESDAY_TASKS for index in range(len(_DAYS))
    ),
    target_hours=42,
)


def slots(instance: Instance) -> tuple[tuple[str, str, str], ...]:
    """Every person, day, and shift the assignment variables cover."""

    return tuple(
        (person, day, shift.name)
        for person in instance.persons
        for day in instance.days
        for shift in instance.shifts_on(day)
    )


def new_model(
    instance: Instance,
    *,
    fixed: dict[tuple[str, str], int] | None = None,
) -> pyo.ConcreteModel:
    """Assignment variables only. Scores and rules are added separately."""

    model = pyo.ConcreteModel()
    model.x = pyo.Var(slots(instance), domain=pyo.Binary)
    if fixed is not None:
        for person, day, shift in slots(instance):
            model.x[person, day, shift].fix(fixed[person, day, shift])
    model.rules = pyo.ConstraintList()
    return model


def build_roster(
    instance: Instance,
    *,
    fixed: dict[tuple[str, str], int] | None = None,
) -> pyo.ConcreteModel:
    """Assignments and both scores, with no objective and no roster rules."""

    model = new_model(instance, fixed=fixed)
    ConsistentSchedule.add(model, instance)
    TargetTime.add(model, instance, target_hours=instance.target_hours)
    return model
