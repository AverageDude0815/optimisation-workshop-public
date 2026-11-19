"""Solve one objective, then re-score the chosen roster on both raw scores."""

import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition

from workshop.black_box_model.reader import read_roster
from workshop.black_box_model.solver import solve
from workshop.model import Instance, RosterScore, build_roster, slots


def evaluate(
    instance: Instance,
    assignments: tuple[tuple[str, str, str], ...] | set[tuple[str, str, str]],
) -> RosterScore | None:
    """Fix one roster and let HiGHS compute both scores. Illegal rosters return None."""

    chosen = set(assignments)
    fixed = {slot: int(slot in chosen) for slot in slots(instance)}
    model = build_roster(instance, fixed=fixed)
    model.objective = pyo.Objective(
        expr=model.consistency_score + model.target_score,
        sense=pyo.maximize,
    )
    condition = solve(model)
    if condition != TerminationCondition.optimal:
        return None
    return read_roster(instance, model)


def solve_objective(instance: Instance, model: pyo.ConcreteModel, objective) -> RosterScore:
    """Maximize one expression, then re-score the chosen roster on both raw scores."""

    expression = objective(model)
    if hasattr(model, "objective"):
        model.del_component(model.objective)
    model.objective = pyo.Objective(expr=expression, sense=pyo.maximize)
    condition = solve(model)
    if condition != TerminationCondition.optimal:
        raise RuntimeError(f"HiGHS returned {condition}")
    solved_objective = float(pyo.value(model.objective))
    expression_value = float(pyo.value(expression))
    chosen = tuple(
        slot for slot in slots(instance) if pyo.value(model.x[slot]) > 0.5
    )
    scored = evaluate(instance, chosen)
    if scored is None:
        raise RuntimeError("the chosen roster could not be scored")
    if abs(solved_objective - expression_value) > 1e-4:
        raise RuntimeError(
            f"solver objective {solved_objective} does not match the roster scores {expression_value}"
        )
    from workshop.visualisation.gantt import show_solved

    show_solved(instance, scored)
    return scored


def run(instance: Instance, objective, *, prepare=None) -> RosterScore:
    """Build both scores, then solve one objective."""

    model = build_roster(instance)
    if prepare is not None:
        prepare(model, instance)
    return solve_objective(instance, model, objective)
