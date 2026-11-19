"""One plain Gantt chart of the roster."""

from workshop.model import WORKSHOP, RosterScore, slots
from workshop.visualisation.gantt import show, show_offered


def test_short_monday_draws_the_worked_shifts(tmp_path):
    roster = RosterScore(
        assignments=(("Alex", "Monday", "08:00"), ("Alex", "Monday", "12:00")),
        hours=8,
        consistency=2,
        target=48,
    )

    path = show(WORKSHOP, roster, open_browser=False, output_dir=tmp_path)
    page = path.read_text()

    assert path.name == "gantt.html"
    assert page.count('class="bar"') == 2
    assert "Alex 8/42" in page
    assert "Sam 0/42" in page
    assert "Consistency 2/24 (8%)" in page
    assert "Target time 48/3528 (1%)" in page
    assert "rgb(" not in page


def test_full_roster_draws_every_assignment(tmp_path):
    assignments = tuple(
        (person, day, shift.name)
        for person in WORKSHOP.persons
        for day in WORKSHOP.days
        for shift in WORKSHOP.shifts_on(day)
    )
    roster = RosterScore(
        assignments=assignments,
        hours=168,
        consistency=24,
        target=3528,
    )

    page = show(WORKSHOP, roster, open_browser=False, output_dir=tmp_path).read_text()

    assert page.count('class="bar"') == len(assignments)
    assert "Consistency 24/24 (100%)" in page
    assert "Target time 3528/3528 (100%)" in page
    assert "rgb(" not in page


def test_offered_tasks_lists_every_person_and_task(tmp_path):
    page = show_offered(WORKSHOP, open_browser=False, output_dir=tmp_path).read_text()

    assert page.count('class="bar"') == len(slots(WORKSHOP))
    for person in WORKSHOP.persons:
        assert person in page
    for day in WORKSHOP.days:
        for shift in WORKSHOP.shifts_on(day):
            assert shift.name in page
    assert "rgb(" not in page
