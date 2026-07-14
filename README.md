# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

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

## 🖥️ Sample Output

Output from running `python main.py`:

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

## 🧪 Testing PawPal+

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

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

All core scheduling behaviors — sorting, recurrence, conflict detection, filtering, and plan generation — are covered with both happy-path and edge-case tests, and all 15 pass. One star held back because `detect_conflicts()` only catches exact-time collisions, not partial/overlapping-duration conflicts (documented as a known limitation in `reflection.md`), so it isn't yet a fully reliable conflict guard for real-world scheduling.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks earliest-to-latest by their `scheduled_time` ("HH:MM") string. |
| Priority/time-budget scheduling | `Scheduler.generate_plan()` | Sorts pending tasks by priority (ties broken by shorter duration first) and greedily fills the owner's `available_minutes`, skipping tasks that don't fit. |
| Filtering | `Scheduler.filter_tasks()` | Filters `(pet, task)` pairs by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that share the same `due_date` + `scheduled_time` as a warning message; does not detect partial/overlapping-duration conflicts (see `reflection.md` 2b for why). |
| Recurring tasks | `Task.get_next_occurrence()`, `Pet.complete_task()` | Completing a "daily"/"weekly" task automatically creates its next occurrence, with `due_date` advanced via `datetime.timedelta`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
