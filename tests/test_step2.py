"""Step 2. The plain sum also forbids a gap inside the day."""

import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition

from workshop.black_box_model.optimize import solve_objective
from workshop.black_box_model.solver import solve
from workshop.model import WORKSHOP, new_model, slots
from workshop.steps.step2 import build_model


def solve_plain_sum():
    model = new_model(WORKSHOP)
    build_model(model, WORKSHOP)
    return solve_objective(
        WORKSHOP,
        model,
        lambda built: built.consistency_score + built.target_score,
    )


def _by_person_day(roster):
    worked = {
        person: {day: set() for day in WORKSHOP.days} for person in WORKSHOP.persons
    }
    for person, day, shift in roster.assignments:
        worked[person][day].add(shift)
    return worked


def _feasible(assignments) -> bool:
    chosen = set(assignments)
    model = new_model(WORKSHOP, fixed={slot: int(slot in chosen) for slot in slots(WORKSHOP)})
    build_model(model, WORKSHOP)
    model.objective = pyo.Objective(expr=0, sense=pyo.maximize)
    return solve(model) == TerminationCondition.optimal


def test_plain_sum_obeys_the_three_rules():
    roster = solve_plain_sum()
    worked = _by_person_day(roster)
    seen = set()
    for person, day, shift in roster.assignments:
        assert (day, shift) not in seen
        seen.add((day, shift))

    for person in WORKSHOP.persons:
        off_run = False
        previous_off = False
        for day in WORKSHOP.days:
            chosen = [shift for shift in WORKSHOP.shifts_on(day) if shift.name in worked[person][day]]
            for earlier, later in zip(chosen, chosen[1:]):
                assert earlier.end_hour == later.start_hour
            assert sum(shift.hours for shift in chosen) <= 8
            is_off = not chosen
            off_run = off_run or (is_off and previous_off)
            previous_off = is_off
        assert off_run


def test_a_gap_inside_the_day_is_rejected():
    assert not _feasible((("Alex", "Monday", "00:00"), ("Alex", "Monday", "08:00")))


def test_more_than_eight_hours_is_rejected():
    assert not _feasible(
        (
            ("Alex", "Monday", "00:00"),
            ("Alex", "Monday", "08:00"),
            ("Alex", "Monday", "12:00"),
        )
    )


def test_a_week_without_two_days_off_is_rejected():
    assert not _feasible(tuple(("Alex", day, "00:00") for day in WORKSHOP.days))


def test_two_people_on_one_task_is_rejected():
    assert not _feasible((("Alex", "Monday", "12:00"), ("Sam", "Monday", "12:00")))


def _double(day: str) -> tuple[str, str]:
    if WORKSHOP.days.index(day) % 2 == 0:
        return ("08:00", "12:00")
    return ("00:00", "04:00")


def test_five_weekdays_of_eight_hours_is_allowed():
    assert _feasible(
        tuple(("Alex", day, shift) for day in WORKSHOP.days[:5] for shift in _double(day))
    )
