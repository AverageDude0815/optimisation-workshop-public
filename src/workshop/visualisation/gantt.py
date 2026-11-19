"""One plain Gantt chart of the roster."""

from __future__ import annotations

import html
import os
import webbrowser
from pathlib import Path

from workshop.model import Instance, RosterScore

_DAY_START = 0
_DAY_SPAN = 24
_OUTPUT = Path("output")


def _bars(instance: Instance, roster: RosterScore) -> list[dict[str, str | float]]:
    shifts = {shift.name: shift for shift in instance.shifts}
    day_index = {day: index for index, day in enumerate(instance.days)}
    bars = []
    for person, day, shift_name in roster.assignments:
        shift = shifts[shift_name]
        left = (day_index[day] + (shift.start_hour - _DAY_START) / _DAY_SPAN) / len(instance.days)
        width = (shift.hours / _DAY_SPAN) / len(instance.days)
        bars.append(
            {
                "person": person,
                "day": day,
                "shift": shift_name,
                "start": shift.start_hour,
                "end": shift.end_hour,
                "left": left * 100,
                "width": width * 100,
            }
        )
    return bars


def _amount(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.1f}"


def _score_line(name: str, actual: float, maximum: float) -> str:
    """``actual/maximum`` as a percentage of that score's peak."""

    percent = 0.0 if maximum == 0 else 100.0 * actual / maximum
    return f"{name} {_amount(actual)}/{_amount(maximum)} ({percent:.0f}%)"


def _scores(instance: Instance, roster: RosterScore) -> str:
    consistency_max = float(
        sum(
            len(instance.persons) * len(instance.shared_shifts(today, tomorrow))
            for today, tomorrow in instance.pairs
        )
    )
    target_max = float(len(instance.persons) * instance.target_hours**2)
    return (
        f"{_score_line('Consistency', roster.consistency, consistency_max)}. "
        f"{_score_line('Target time', roster.target, target_max)}."
    )


def _page(title: str, scores: str, legend: str, rows_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
  body {{ font-family: sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 20px; }}
  .scores {{ margin-bottom: 4px; font-size: 16px; }}
  .legend {{ margin-top: 0; margin-bottom: 16px; }}
  .chart {{ display: grid; grid-template-columns: 120px 1fr; gap: 8px; align-items: center; }}
  .lane {{ position: relative; height: 48px; background: #f4f4f4; border: 1px solid #ccc; }}
  .bar {{ position: absolute; top: 8px; height: 32px; background: #222; box-sizing: border-box; }}
  .ticks {{ position: relative; height: 18px; font-size: 12px; }}
  .tick {{ position: absolute; transform: translateX(-50%); white-space: nowrap; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<p class="scores">{html.escape(scores)}</p>
<p class="legend">{legend}</p>
<div class="chart">
{rows_html}
</div>
</body>
</html>
"""


def _ticks(instance: Instance) -> str:
    parts = []
    for index, day in enumerate(instance.days):
        left = (index + 0.5) / len(instance.days) * 100
        parts.append(f'<span class="tick" style="left:{left:.2f}%">{html.escape(day[:3])}</span>')
    return "".join(parts)


def _write(
    path: Path, title: str, scores: str, legend: str, rows_html: str, *, open_browser: bool
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_page(title, scores, legend, rows_html), encoding="utf-8")
    print(f"Gantt: {path}")
    if open_browser:
        webbrowser.open(path.resolve().as_uri())


def show(
    instance: Instance,
    roster: RosterScore,
    *,
    open_browser: bool = True,
    output_dir: Path = _OUTPUT,
) -> Path:
    """Write the roster chart and open it in the browser."""

    bars = _bars(instance, roster)
    ticks = _ticks(instance)
    hours_of = {shift.name: shift.hours for shift in instance.shifts}
    person_hours = {person: 0.0 for person in instance.persons}
    for person, _day, shift in roster.assignments:
        person_hours[person] += hours_of[shift]
    rows = []
    for index, person in enumerate(instance.persons):
        bits = []
        for bar in bars:
            if bar["person"] != person:
                continue
            label = (
                f"{person} {bar['day']} {bar['shift']}–{int(bar['end']):02d}:00. "
                f"Hours {person_hours[person]:.0f} / {instance.target_hours:.0f}"
            )
            style = f"left:{bar['left']:.2f}%;width:{bar['width']:.2f}%"
            bits.append(
                f'<div class="bar" style="{style}" title="{html.escape(label)}"></div>'
            )
        tick_row = f'<div class="ticks">{ticks}</div>' if index == 0 else ""
        rows.append(
            f"<div>{html.escape(person)}</div><div>{tick_row}"
            f'<div class="lane">{"".join(bits)}</div></div>'
        )
    legend = ", ".join(
        f"{person} {person_hours[person]:.0f}/{instance.target_hours:.0f}"
        for person in instance.persons
    )
    path = output_dir / "gantt.html"
    _write(
        path,
        "Roster",
        _scores(instance, roster),
        legend,
        "".join(rows),
        open_browser=open_browser,
    )
    return path


def show_offered(
    instance: Instance,
    *,
    open_browser: bool = True,
    output_dir: Path = _OUTPUT,
) -> Path:
    """Write every offered task on every person's lane and open the chart."""

    assignments = tuple(
        (person, day, shift.name)
        for person in instance.persons
        for day in instance.days
        for shift in instance.shifts_on(day)
    )
    roster = RosterScore(assignments=assignments, hours=0, consistency=0, target=0)
    bars = _bars(instance, roster)
    ticks = _ticks(instance)
    rows = []
    for index, person in enumerate(instance.persons):
        bits = []
        for bar in bars:
            if bar["person"] != person:
                continue
            label = f"{person} {bar['day']} {bar['shift']}–{int(bar['end']):02d}:00"
            style = f"left:{bar['left']:.2f}%;width:{bar['width']:.2f}%"
            bits.append(f'<div class="bar" style="{style}" title="{html.escape(label)}"></div>')
        tick_row = f'<div class="ticks">{ticks}</div>' if index == 0 else ""
        rows.append(
            f"<div>{html.escape(person)}</div><div>{tick_row}"
            f'<div class="lane">{"".join(bits)}</div></div>'
        )
    persons = ", ".join(instance.persons)
    print(f"Persons: {persons}")
    for day in instance.days:
        tasks = ", ".join(
            f"{shift.name}–{shift.end_hour:02d}:00" for shift in instance.shifts_on(day)
        )
        print(f"{day}: {tasks}")
    path = output_dir / "tasks.html"
    _write(
        path,
        "Offered tasks",
        f"Persons: {persons}",
        "Every bar is a task any of these persons can take.",
        "".join(rows),
        open_browser=open_browser,
    )
    return path


def show_solved(instance: Instance, roster: RosterScore) -> None:
    """Open the chart unless a test is running."""

    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    show(instance, roster)
