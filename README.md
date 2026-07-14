# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks across one or more pets —
sorting, filtering, recurring tasks, conflict detection, and a time-budgeted daily plan.

## Features

- **Multi-pet task tracking** — add pets and tasks (title, duration, priority, category, scheduled time, frequency)
- **Priority/time-budget scheduling** — `Scheduler.generate_plan()` fills the owner's available minutes with the
  highest-priority tasks first, skipping (and explaining why) any that don't fit
- **Sorting by time** — `Scheduler.sort_by_time()` lists every task chronologically by `scheduled_time`
- **Filtering** — `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status
- **Daily recurrence** — `Task.get_next_occurrence()` / `Pet.complete_task()` automatically creates the next
  occurrence when a `"daily"` or `"weekly"` task is marked complete
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two tasks scheduled at the same date and time
- **Automated test suite** — 15 pytest tests covering happy paths and edge cases for every algorithm above

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Sample Output

Output from running `python main.py` — see the [Demo Walkthrough](#demo-walkthrough) below for the full run
including sorting, filtering, recurrence, and conflict detection.

```
Today's Schedule for Jordan (90 min available):

[OK] Mochi: Evening meds (5 min) - Included: high priority, fits in remaining 90 min
[OK] Mochi: Breakfast (10 min) - Included: high priority, fits in remaining 85 min
[OK] Whiskers: Feeding (10 min) - Included: high priority, fits in remaining 75 min
[OK] Mochi: Morning walk (30 min) - Included: high priority, fits in remaining 65 min
[OK] Whiskers: Litter box cleaning (10 min) - Included: medium priority, fits in remaining 35 min
[OK] Whiskers: Brushing (15 min) - Included: low priority, fits in remaining 25 min
[SKIP] Mochi: Fetch in the yard (40 min) - Skipped: needs 40 min, only 10 min remaining
```

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 15 tests) covers:

- **Core behaviors**: marking a task complete, adding a task to a pet
- **Sorting**: tasks are returned in chronological order by `scheduled_time`, including the empty-list edge case
- **Recurrence**: completing a `"daily"` task creates a next-day occurrence; a non-recurring task creates nothing
- **Conflict detection**: two tasks at the same `due_date` + `scheduled_time` are flagged, tasks at the same time on *different* dates are not, and no-conflict cases return an empty list
- **Filtering**: filtering `(pet, task)` pairs by pet name and/or completion status, including a no-match edge case
- **Plan generation**: tasks that don't fit the owner's available time are skipped, completed tasks are excluded, and an owner with no pets produces an empty plan

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
collecting ... collected 15 items

tests/test_pawpal.py::test_task_mark_complete_changes_status PASSED      [  6%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 13%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 20%]
tests/test_pawpal.py::test_sort_by_time_handles_empty_list PASSED        [ 26%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 33%]
tests/test_pawpal.py::test_completing_task_with_no_recurrence_creates_nothing PASSED [ 40%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_at_same_date_and_time PASSED [ 46%]
tests/test_pawpal.py::test_detect_conflicts_ignores_same_time_on_different_dates PASSED [ 53%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_list_when_no_overlaps PASSED [ 60%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 66%]
tests/test_pawpal.py::test_filter_tasks_by_completed_status PASSED       [ 73%]
tests/test_pawpal.py::test_filter_tasks_with_no_matching_pet_returns_empty_list PASSED [ 80%]
tests/test_pawpal.py::test_generate_plan_skips_tasks_that_dont_fit_available_time PASSED [ 86%]
tests/test_pawpal.py::test_generate_plan_excludes_already_completed_tasks PASSED [ 93%]
tests/test_pawpal.py::test_generate_plan_handles_owner_with_no_pets PASSED [100%]

============================== 15 passed in 0.05s ===============================
```

**Confidence Level:** 4/5

All core scheduling behaviors — sorting, recurrence, conflict detection, filtering, and plan generation — are covered with both happy-path and edge-case tests, and all 15 pass. One star held back because `detect_conflicts()` only catches exact-time collisions, not partial/overlapping-duration conflicts (documented as a known limitation in `reflection.md`), so it isn't yet a fully reliable conflict guard for real-world scheduling.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks earliest-to-latest by their `scheduled_time` ("HH:MM") string. |
| Priority/time-budget scheduling | `Scheduler.generate_plan()` | Sorts pending tasks by priority (ties broken by shorter duration first) and greedily fills the owner's `available_minutes`, skipping tasks that don't fit. |
| Filtering | `Scheduler.filter_tasks()` | Filters `(pet, task)` pairs by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that share the same `due_date` + `scheduled_time` as a warning message; does not detect partial/overlapping-duration conflicts (see `reflection.md` 2b for why). |
| Recurring tasks | `Task.get_next_occurrence()`, `Pet.complete_task()` | Completing a "daily"/"weekly" task automatically creates its next occurrence, with `due_date` advanced via `datetime.timedelta`. |

## Demo Walkthrough

**UI features (`app.py`):**

- Add pets (name + species) and tasks (title, duration, priority, scheduled time, frequency) to any pet
- Mark a task done with the "Mark done" button — recurring (`daily`/`weekly`) tasks automatically spawn their
  next occurrence, shown via a toast with the new due date
- View **all tasks sorted by time** in one table
- **Filter tasks** by pet and/or completion status
- See **conflict warnings** whenever two tasks share the same date and time, or a success message
  when there are none
- Click **Generate schedule** to build today's time-budgeted plan — included tasks show as green success
  messages, skipped ones as yellow warnings explaining why

**Example workflow:**

1. Add pet "Mochi" (dog) and pet "Whiskers" (cat).
2. Add Mochi's tasks: "Morning walk" (30 min, high priority, 08:00, daily), "Breakfast" (10 min, high, 08:30).
3. Add Whiskers' task "Play session" (15 min, medium, 08:30) — same time as Mochi's breakfast.
4. Check the **Scheduling Conflicts** section — it flags the 08:30 clash between the two pets.
5. Click **Generate schedule** — high-priority tasks are scheduled first within the owner's available minutes;
   anything that doesn't fit is skipped with a reason.
6. Mark "Morning walk" done — since it's `daily`, a new occurrence is created for tomorrow automatically.

**Key Scheduler behaviors shown:** priority/time-budget planning (`generate_plan`), chronological sorting
(`sort_by_time`), pet/status filtering (`filter_tasks`), daily recurrence (`get_next_occurrence` /
`complete_task`), and same-slot conflict detection (`detect_conflicts`).

**Sample CLI output** (`python main.py`), demonstrating the same algorithms outside the UI:

```
Today's Schedule for Jordan (90 min available):

[OK] Mochi: Evening meds (5 min) - Included: high priority, fits in remaining 90 min
[OK] Mochi: Breakfast (10 min) - Included: high priority, fits in remaining 85 min
[OK] Whiskers: Feeding (10 min) - Included: high priority, fits in remaining 75 min
[OK] Mochi: Morning walk (30 min) - Included: high priority, fits in remaining 65 min
[OK] Whiskers: Litter box cleaning (10 min) - Included: medium priority, fits in remaining 35 min
[OK] Whiskers: Brushing (15 min) - Included: low priority, fits in remaining 25 min
[SKIP] Mochi: Fetch in the yard (40 min) - Skipped: needs 40 min, only 10 min remaining

All tasks sorted by scheduled time:

08:00 - Morning walk
08:15 - Feeding
08:30 - Breakfast
12:00 - Litter box cleaning
17:00 - Fetch in the yard
19:30 - Evening meds
20:00 - Brushing

Filtered: Mochi's tasks only:

Mochi: Morning walk
Mochi: Evening meds
Mochi: Breakfast
Mochi: Fetch in the yard

Filtered: incomplete tasks only:

Mochi: Morning walk
Mochi: Evening meds
Mochi: Breakfast
Mochi: Fetch in the yard
Whiskers: Brushing
Whiskers: Feeding
Whiskers: Litter box cleaning

Completing 'Morning walk' (due 2026-07-14, frequency=daily)
Completed: True
Next occurrence created for 2026-07-15 (completed=False)

Checking for scheduling conflicts:

WARNING: Conflict on 2026-07-14 at 08:30: Mochi's 'Breakfast', Whiskers's 'Play session'
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
