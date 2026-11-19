"""The roster instance and its assignment variables."""

from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo

from workshop.objective.consistent_schedule import ConsistentSchedule
from workshop.objective.target_time import TargetTime


@dataclass(frozen=True)
class Shift:
    """One task a person can take.

    Attributes:
        name: The label used to look the task up, such as ``"08:00"``.
        start_hour: When it starts, as an hour from midnight. ``8`` is 08:00.
        hours: How long it lasts. Every task in this workshop lasts 4 hours.
        end_hour: ``start_hour + hours``. The next task abuts this one when
            its ``start_hour`` equals this value. A later start leaves a gap,
            even if no task is offered in between.
    """

    name: str
    start_hour: int
    hours: float

    @property
    def end_hour(self) -> int:
        return self.start_hour + int(self.hours)


@dataclass(frozen=True)
class Instance:
    """The fixed roster. This is ordinary Python, not a Pyomo object.

    Pyomo is the library that will choose the roster. The thing it chooses
    is stored on the model, not here. Everything on an ``Instance`` is data
    you can read while you write the step: names, hours, and which tasks
    exist on which day.

    Attributes:
        days: Day names from Monday through Sunday, in calendar order.
        persons: The people who can be scheduled. This workshop has Alex and Sam.
        shifts_by_day: One tuple of tasks per day, in the same order as
            ``days``. A task left off a day cannot be worked that day.
        target_hours: The hour total each person is scored against. One
            person's target-time reward peaks when their hours equal this
            number. The workshop uses 42.

    Derived values:

    - ``pairs``: consecutive days, each entry ``(today, tomorrow)``. Sunday
      does not pair with Monday. The week does not wrap.
    - ``shifts_on(day)``: that day's tasks, earliest start first. Each item
      is a ``Shift``.
    - ``shared_shifts(today, tomorrow)``: tasks offered on both days. The
      consistent-schedule score only has a term for these starts.
    - ``shifts``: every distinct task in the week, ordered by start time.
      This is the catalog. A start can be in the catalog and still be
      missing on some days, so it is the wrong list when a day matters.
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
        """Tasks offered on ``day``, earliest start first.

        Args:
            day: A name from ``days``, such as ``"Monday"``.

        Returns:
            The tasks that exist that day. A task that is not in this tuple
            cannot be worked on ``day``.
        """

        ordered = sorted(
            self.shifts_by_day[self.days.index(day)], key=lambda shift: shift.start_hour
        )
        return tuple(ordered)

    def shared_shifts(self, today: str, tomorrow: str) -> tuple[Shift, ...]:
        """Tasks offered on both days.

        The consistent-schedule score has one term per person for each of
        these starts, and no term for a start that exists on only one of
        the two days.

        Args:
            today: The earlier day of a consecutive pair.
            tomorrow: The next day. Take pairs from ``pairs``. The week does
                not wrap from Sunday back to Monday.

        Returns:
            The shared tasks, earliest start first.
        """

        tomorrow_names = {shift.name for shift in self.shifts_on(tomorrow)}
        return tuple(shift for shift in self.shifts_on(today) if shift.name in tomorrow_names)

    @property
    def shifts(self) -> tuple[Shift, ...]:
        """Every distinct task in the week, earliest start first.

        This is the catalog, not one day's offer. ``"04:00"`` is in the
        catalog because Tuesday has it, and it is still absent on Monday.
        Use ``shifts_on`` or ``shared_shifts`` when the day matters.
        """

        by_name: dict[str, Shift] = {}
        for day_shifts in self.shifts_by_day:
            for shift in day_shifts:
                by_name.setdefault(shift.name, shift)
        return tuple(sorted(by_name.values(), key=lambda shift: shift.start_hour))

    @property
    def pairs(self) -> tuple[tuple[str, str], ...]:
        """Consecutive days, each entry ``(today, tomorrow)``.

        Monday with Tuesday is a pair. Sunday with Monday is not. The week
        does not wrap.
        """

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
    """Every assignment the model is allowed to make.

    Args:
        instance: The fixed roster. Only tasks returned by ``shifts_on``
            for that day are included.

    Returns:
        Tuples ``(person, day, shift_name)``. ``model.x`` has one 0-or-1
        decision for each of these.
    """

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
    """Create the Pyomo problem with decisions and an empty rule list.

    A ``ConcreteModel`` is one concrete optimisation problem: decisions,
    rules, and later a score to maximise. This function only creates the
    decisions. The step files attach the scores and the roster rules.

    ``model.x[person, day, shift_name]`` is 1 when that person works that
    task on that day, and 0 otherwise. The solver picks those values. While
    you are still building the model, ``x`` is a symbol, not a Python number,
    so do not read it with ``int`` or ``if``.

    ``model.rules`` is the list the rules are added to. It starts empty.

    Args:
        instance: Who can work, on which days, and which tasks exist.
        fixed: Optional forced decisions for tests, mapping
            ``(person, day, shift_name)`` to 0 or 1.

    Returns:
        A model with ``x`` and ``rules``, and no scores yet.
    """

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
