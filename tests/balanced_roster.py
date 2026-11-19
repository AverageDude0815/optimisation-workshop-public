"""Shared solve setup for steps 3, 4, and 5."""

from workshop.model import WORKSHOP, new_model
from workshop.steps.step2 import build_model


def model_with_rule():
    model = new_model(WORKSHOP)
    build_model(model, WORKSHOP)
    return model


def objective_percentages(roster) -> tuple[float, float]:
    """Consistency and target time as percentages of their formula peaks."""

    consistency_max = sum(
        len(WORKSHOP.persons) * len(WORKSHOP.shared_shifts(today, tomorrow))
        for today, tomorrow in WORKSHOP.pairs
    )
    target_max = len(WORKSHOP.persons) * WORKSHOP.target_hours**2
    return (
        100.0 * roster.consistency / consistency_max,
        100.0 * roster.target / target_max,
    )


def assert_both_objectives_above_90(roster) -> None:
    consistency, target = objective_percentages(roster)
    assert consistency > 90, f"consistency is {consistency:.1f}%"
    assert target > 90, f"target time is {target:.1f}%"


def assert_consistency_above_95_and_target_above_75(roster) -> None:
    consistency, target = objective_percentages(roster)
    assert consistency > 95, f"consistency is {consistency:.1f}%"
    assert target > 75, f"target time is {target:.1f}%"
