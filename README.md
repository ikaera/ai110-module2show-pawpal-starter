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
- **Next available slot finder** — `Scheduler.find_next_available_slot()` finds the earliest open gap in a
  pet's day that's long enough for a new task *(optional extension)*
- **Data persistence** — `Owner.save_to_json()` / `Owner.load_from_json()` save/restore pets and tasks to/from
  `data.json` so nothing is lost between app runs *(optional extension)*
- **Automated test suite** — 21 pytest tests covering happy paths and edge cases for every algorithm above

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

The suite (`tests/test_pawpal.py`, 21 tests) covers:

- **Core behaviors**: marking a task complete, adding a task to a pet
- **Sorting**: tasks are returned in chronological order by `scheduled_time`, including the empty-list edge case
- **Recurrence**: completing a `"daily"` task creates a next-day occurrence; a non-recurring task creates nothing
- **Conflict detection**: two tasks at the same `due_date` + `scheduled_time` are flagged, tasks at the same time on *different* dates are not, and no-conflict cases return an empty list
- **Filtering**: filtering `(pet, task)` pairs by pet name and/or completion status, including a no-match edge case
- **Plan generation**: tasks that don't fit the owner's available time are skipped, completed tasks are excluded, and an owner with no pets produces an empty plan
- **Next available slot**: finds the gap between two tasks, returns `None` when the day is fully booked, and ignores completed tasks when checking for conflicts
- **Persistence**: saving and reloading an owner (with pets, tasks, and a completed task) round-trips correctly, loading a missing file raises `FileNotFoundError`, and an owner with no pets saves/loads cleanly

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 21 items

tests/test_pawpal.py::test_task_mark_complete_changes_status PASSED      [  4%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  9%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 14%]
tests/test_pawpal.py::test_sort_by_time_handles_empty_list PASSED        [ 19%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 23%]
tests/test_pawpal.py::test_completing_task_with_no_recurrence_creates_nothing PASSED [ 28%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_at_same_date_and_time PASSED [ 33%]
tests/test_pawpal.py::test_detect_conflicts_ignores_same_time_on_different_dates PASSED [ 38%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_list_when_no_overlaps PASSED [ 42%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 47%]
tests/test_pawpal.py::test_filter_tasks_by_completed_status PASSED       [ 52%]
tests/test_pawpal.py::test_filter_tasks_with_no_matching_pet_returns_empty_list PASSED [ 57%]
tests/test_pawpal.py::test_generate_plan_skips_tasks_that_dont_fit_available_time PASSED [ 61%]
tests/test_pawpal.py::test_generate_plan_excludes_already_completed_tasks PASSED [ 66%]
tests/test_pawpal.py::test_generate_plan_handles_owner_with_no_pets PASSED [ 71%]
tests/test_pawpal.py::test_find_next_available_slot_returns_gap_between_tasks PASSED [ 76%]
tests/test_pawpal.py::test_find_next_available_slot_returns_none_when_day_is_full PASSED [ 80%]
tests/test_pawpal.py::test_find_next_available_slot_ignores_completed_tasks PASSED [ 85%]
tests/test_pawpal.py::test_save_and_load_json_round_trip PASSED          [ 90%]
tests/test_pawpal.py::test_load_from_json_missing_file_raises PASSED     [ 95%]
tests/test_pawpal.py::test_save_to_json_handles_owner_with_no_pets PASSED [100%]

============================= 21 passed in 0.07s ===============================
```

**Confidence Level:** 4/5

All core scheduling behaviors — sorting, recurrence, conflict detection, filtering, plan generation, next-available-slot lookup, and JSON persistence — are covered with both happy-path and edge-case tests, and all 21 pass. One star held back because `detect_conflicts()` only catches exact-time collisions, not partial/overlapping-duration conflicts (documented as a known limitation in `reflection.md`), so it isn't yet a fully reliable conflict guard for real-world scheduling.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks earliest-to-latest by their `scheduled_time` ("HH:MM") string. |
| Priority/time-budget scheduling | `Scheduler.generate_plan()` | Sorts pending tasks by priority (ties broken by shorter duration first) and greedily fills the owner's `available_minutes`, skipping tasks that don't fit. |
| Filtering | `Scheduler.filter_tasks()` | Filters `(pet, task)` pairs by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that share the same `due_date` + `scheduled_time` as a warning message; does not detect partial/overlapping-duration conflicts (see `reflection.md` 2b for why). |
| Recurring tasks | `Task.get_next_occurrence()`, `Pet.complete_task()` | Completing a "daily"/"weekly" task automatically creates its next occurrence, with `due_date` advanced via `datetime.timedelta`. |
| Next available slot *(optional extension)* | `Scheduler.find_next_available_slot()` | Converts every task's `scheduled_time` to minutes-since-midnight, walks the gaps between them (and before the first / after the last), and returns the earliest "HH:MM" gap that's at least as long as the requested duration, or `None` if the day (bounded by `day_start`/`day_end`) has no room left. Ignores completed tasks. |
| Data persistence *(optional extension)* | `Owner.save_to_json()`, `Owner.load_from_json()` | Serializes the full owner → pets → tasks tree to `data.json` and rebuilds it on load, so pets and tasks survive between app runs. See [Data Persistence](#data-persistence) below. |

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
- Click **Find next available slot** *(optional extension)* to get the earliest open gap today that's long
  enough for a new task of the given duration

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

Finding next available 20-minute slot for Mochi today:

Next available slot: 08:45

Saved Jordan's data to demo_data.json.
Reloaded owner 'Jordan' with 2 pets and 9 total tasks.
```

## Optional Extension: Next Available Slot Finder

`Scheduler.find_next_available_slot(owner, due_date, duration_minutes, day_start="08:00", day_end="21:00")`
answers a question the other algorithms don't: *"if I need to squeeze in a new N-minute task today, where's
the first open gap?"* It's available both in the CLI demo (`main.py`) and as a "Find next available slot"
button in the Streamlit UI (`app.py`).

**How it works:** every non-completed task due on `due_date` is sorted by `scheduled_time` and converted to
minutes-since-midnight. The method walks the gaps between consecutive tasks (plus the gap before the first
task and after the last, bounded by `day_start`/`day_end`) and returns the earliest "HH:MM" gap that's at
least `duration_minutes` long. If nothing fits, it returns `None`.

**Files modified:** `pawpal_system.py` (new `Scheduler.find_next_available_slot` method), `main.py` (CLI demo),
`app.py` (UI section), `tests/test_pawpal.py` (3 new tests).

**Sample CLI output**, given Mochi's day (Morning walk 08:00-08:30, Breakfast 08:30-08:40, Evening meds 19:30,
Fetch in the yard 17:00-17:40):

```
Finding next available 20-minute slot for Mochi today:

Next available slot: 08:45
```

If the day were completely booked from `day_start` to `day_end`, the same call would print:

```
Finding next available 20-minute slot for Mochi today:

No slot available today.
```

## Optional Extension: Data Persistence

By default, everything an owner builds up in the Streamlit app — pets, tasks, priorities, completion status —
disappears the moment the app process restarts, because it only lives in `st.session_state`. This extension
adds a `data.json` file so that state survives between runs.

**How it works — the persistence workflow:**

1. Every model class gets a matching pair of methods: `to_dict()` converts an instance (and everything it
   owns) into plain dicts/lists/strings that `json.dump` can handle, and `from_dict()` rebuilds an instance
   from that same shape.
   - `Task.to_dict()` / `Task.from_dict()` handle the one tricky field: `due_date` is a `datetime.date`
     object, which isn't JSON-serializable on its own, so it's stored as an ISO string (`date.isoformat()`)
     and parsed back with `date.fromisoformat()`.
   - `Pet.to_dict()` / `Pet.from_dict()` nest a list of `Task` dicts.
   - `Owner.to_dict()` / `Owner.from_dict()` nest a list of `Pet` dicts — so one call serializes the entire
     owner → pets → tasks tree.
2. `Owner.save_to_json(filepath="data.json")` calls `self.to_dict()` and writes the result with `json.dump`.
3. `Owner.load_from_json(filepath="data.json")` (a classmethod) reads the file with `json.load` and calls
   `Owner.from_dict()` to reconstruct a live `Owner` object, including all of its `Pet` and `Task` objects.
4. In `app.py`, the owner is loaded from `data.json` on first run of a session (if the file exists) instead of
   always starting blank, and `owner.save_to_json()` is called immediately after every mutation — adding a
   pet, adding a task, marking a task done — so the file is always up to date. `main.py` has a small demo
   that saves to a throwaway `demo_data.json`, reloads it, prints the counts, and deletes the file again.

A **custom dictionary conversion** was used instead of a library like `marshmallow`: the object graph here is
shallow (three classes, one level of nesting each) and every field is already a JSON-friendly type except
`due_date`, so a schema library would add a dependency and boilerplate without solving a real problem. If the
`Task`/`Pet`/`Owner` models grow much more nested or gain more custom types, revisiting that decision would be
reasonable.

**Files modified:** `pawpal_system.py` (`to_dict`/`from_dict` on `Task`, `Pet`, `Owner`; `save_to_json`/
`load_from_json` on `Owner`), `app.py` (load on session start, save after every mutation), `main.py` (save/
reload demo), `tests/test_pawpal.py` (3 new tests: round-trip, missing file, no-pets edge case), `.gitignore`
(excludes the runtime `data.json` — it's user data, not source).

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
