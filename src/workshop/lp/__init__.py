"""LP normalisation. Relax the discrete variables, then take one maximum per score."""

import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition
from pyomo.contrib.appsi.solvers.highs import Highs


def relax_discrete_variables(model: pyo.ConcreteModel) -> list[tuple]:
    """Turn every binary and integer variable into a nonnegative continuous one."""

    relaxed = []
    for variable in model.component_data_objects(pyo.Var, descend_into=True):
        if not (variable.is_binary() or variable.is_integer()):
            continue
        lower, upper = variable.lb, variable.ub
        relaxed.append((variable, variable.domain, lower, upper))
        variable.domain = pyo.NonNegativeReals
        variable.setlb(lower)
        variable.setub(upper)
    return relaxed


def restore_discrete_variables(relaxed: list[tuple]) -> None:
    for variable, domain, lower, upper in relaxed:
        variable.domain = domain
        variable.setlb(lower)
        variable.setub(upper)


def require_continuous(model: pyo.ConcreteModel) -> None:
    still_discrete = [
        variable
        for variable in model.component_data_objects(pyo.Var, descend_into=True)
        if variable.is_binary() or variable.is_integer()
    ]
    if still_discrete:
        raise RuntimeError("the LP model still has discrete variables")


def lp_maximum(model: pyo.ConcreteModel, expression) -> float:
    """Maximize one expression with a fresh LP solve. The model must already be continuous."""

    if hasattr(model, "objective"):
        model.del_component(model.objective)
    model.objective = pyo.Objective(expr=expression, sense=pyo.maximize)
    solver = Highs()
    solver.config.load_solution = False
    solver.config.stream_solver = False
    results = solver.solve(model)
    if results.termination_condition != TerminationCondition.optimal:
        raise RuntimeError(f"HiGHS returned {results.termination_condition}")
    solver.load_vars()
    return float(pyo.value(expression))
