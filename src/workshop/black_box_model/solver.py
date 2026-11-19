"""HiGHS solves."""

import pyomo
import pyomo.environ as pyo
from pyomo.contrib.appsi.base import TerminationCondition
from pyomo.contrib.appsi.solvers.highs import Highs

_SOLVER: Highs | None = None


def _highs() -> Highs:
    global _SOLVER
    if _SOLVER is None:
        _SOLVER = Highs()
        _SOLVER.config.load_solution = False
        _SOLVER.config.stream_solver = False
        _SOLVER.config.mip_gap = 0.0
    return _SOLVER


def solve(model: pyo.ConcreteModel) -> TerminationCondition:
    """Solve with HiGHS and load the variable values when the solve is optimal."""

    solver = _highs()
    results = solver.solve(model)
    if results.termination_condition == TerminationCondition.optimal:
        solver.load_vars()
    return results.termination_condition


def solver_label() -> str:
    version = ".".join(str(part) for part in _highs().version())
    return f"Pyomo {pyomo.__version__} / HiGHS {version}"
