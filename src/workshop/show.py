"""Solve one step and open its Gantt chart."""

import sys

from workshop.black_box_model.optimize import solve_objective
from workshop.lp import relax_discrete_variables, require_continuous, restore_discrete_variables
from workshop.model import WORKSHOP, new_model
from workshop.steps.step1 import build_model as build_step1
from workshop.steps.step2 import build_model as build_step2
from workshop.steps.step3 import objective_weights
from workshop.steps.step4 import (
    normalize_consistent_schedule,
    normalize_target_time,
    objective_weights as step4_weights,
)
from workshop.steps.step5 import lp_divisors, objective_weights as step5_weights


def _model(build):
    model = new_model(WORKSHOP)
    build(model, WORKSHOP)
    return model


def _plain(model):
    return model.consistency_score + model.target_score


def step_1():
    return solve_objective(WORKSHOP, _model(build_step1), _plain)


def step_2():
    return solve_objective(WORKSHOP, _model(build_step2), _plain)


def step_3():
    consistency_weight, target_weight = objective_weights()
    return solve_objective(
        WORKSHOP,
        _model(build_step2),
        lambda model: (
            consistency_weight * model.consistency_score + target_weight * model.target_score
        ),
    )


def step_4():
    consistency_weight, target_weight = step4_weights()
    consistency_divisor = normalize_consistent_schedule(WORKSHOP)
    target_divisor = normalize_target_time(WORKSHOP)
    return solve_objective(
        WORKSHOP,
        _model(build_step2),
        lambda model: (
            consistency_weight * model.consistency_score / consistency_divisor
            + target_weight * model.target_score / target_divisor
        ),
    )


def step_5():
    reference = _model(build_step2)
    relaxed = relax_discrete_variables(reference)
    try:
        require_continuous(reference)
        consistency_divisor, target_divisor = lp_divisors(reference)
    finally:
        restore_discrete_variables(relaxed)
    consistency_weight, target_weight = step5_weights()
    return solve_objective(
        WORKSHOP,
        _model(build_step2),
        lambda model: (
            consistency_weight * model.consistency_score / consistency_divisor
            + target_weight * model.target_score / target_divisor
        ),
    )


def main() -> None:
    steps = {"1": step_1, "2": step_2, "3": step_3, "4": step_4, "5": step_5}
    number = sys.argv[1] if len(sys.argv) > 1 else ""
    if number == "rooster":
        from workshop.visualisation.gantt import show_offered

        show_offered(WORKSHOP)
        return
    if number not in steps:
        raise SystemExit("usage: python -m workshop.show 1|2|3|4|5|rooster")
    roster = steps[number]()
    print(
        f"step {number}: hours={roster.hours} "
        f"consistency={roster.consistency} target={roster.target}"
    )
    for person in WORKSHOP.persons:
        worked = sorted(
            {day for owner, day, _shift in roster.assignments if owner == person},
            key=WORKSHOP.days.index,
        )
        print(f"  {person}: {', '.join(worked) if worked else 'no days'}")


if __name__ == "__main__":
    main()
