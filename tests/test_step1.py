"""Step 1. With the rules, the plain sum stays inside them."""

import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition

from workshop.black_box_model.optimize import solve_objective
from workshop.black_box_model.solver import solve as solve_model
from workshop.model import WORKSHOP, new_model, slots
from workshop.steps.step1 import build_model


def solve():
    model = new_model(WORKSHOP)
    build_model(model, WORKSHOP)
    return solve_objective(
        WORKSHOP,
        model,
        lambda built: built.consistency_score + built.target_score,
    )


def test_plain_sum_obeys_the_rules():
    roster = solve()
    worked = {person: {day: set() for day in WORKSHOP.days} for person in WORKSHOP.persons}
    seen = set()
    for person, day, shift in roster.assignments:
        worked[person][day].add(shift)
        assert (day, shift) not in seen
        seen.add((day, shift))

    for person in WORKSHOP.persons:
        off_run = False
        previous_off = False
        for day in WORKSHOP.days:
            chosen = [shift for shift in WORKSHOP.shifts_on(day) if shift.name in worked[person][day]]
            assert sum(shift.hours for shift in chosen) <= 8
            is_off = not chosen
            off_run = off_run or (is_off and previous_off)
            previous_off = is_off
        assert off_run


def test_a_gap_inside_the_day_is_allowed():
    chosen = {("Alex", "Monday", "00:00"), ("Alex", "Monday", "08:00")}
    model = new_model(WORKSHOP, fixed={slot: int(slot in chosen) for slot in slots(WORKSHOP)})
    build_model(model, WORKSHOP)
    model.objective = pyo.Objective(expr=0, sense=pyo.maximize)
    assert solve_model(model) == TerminationCondition.optimal
