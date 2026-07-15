# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks across one or more pets —
sorting, filtering, recurring tasks, conflict detection, and a time-budgeted daily plan.

## Features

- **Multi-pet task tracking** — add pets and tasks (title, duration, priority, category, scheduled time, frequency)
- **Priority/time-budget scheduling** — `Scheduler.generate_plan()` fills the owner's available minutes with the
  highest-priority tasks first, skipping (and explaining why) any that don't fit
- **Sorting by time** — `Scheduler.sort_by_time()` lists every task chronologically by `scheduled_time`
- **Priority-based scheduling** — `Scheduler.sort_by_priority_then_time()` sorts every task by priority
  (high → medium → low), breaking ties within the same priority by `scheduled_time` *(optional extension)*
- **Filtering** — `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status
- **Daily recurrence** — `Task.get_next_occurrence()` / `Pet.complete_task()` automatically creates the next
  occurrence when a `"daily"` or `"weekly"` task is marked complete
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two tasks scheduled at the same date and time
- **Next available slot finder** — `Scheduler.find_next_available_slot()` finds the earliest open gap in a
  pet's day that's long enough for a new task *(optional extension)*
- **Data persistence** — `Owner.save_to_json()` / `Owner.load_from_json()` save/restore pets and tasks to/from
  `data.json` so nothing is lost between app runs *(optional extension)*
- **Professional formatting** — category emojis, color-coded priority indicators, completion checkmarks, and
  `tabulate`-powered CLI tables make output easier to scan at a glance *(optional extension)*
- **Weekly task rescheduling** — `Scheduler.reschedule_weekly_task()` nudges a recurring task's next
  occurrence forward, day-by-day if needed, to avoid colliding with another task *(optional extension)*
- **Automated test suite** — 29 pytest tests covering happy paths and edge cases for every algorithm above

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

Status    Pet       Task                 Category      Priority    Duration    Reason
--------  --------  -------------------  ------------  ----------  ----------  ---------------------------------------------------
✅ OK      Mochi     Evening meds         💊 meds        🔴 HIGH      5 min       Included: high priority, fits in remaining 90 min
✅ OK      Mochi     Breakfast            🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 85 min
✅ OK      Whiskers  Feeding              🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 75 min
✅ OK      Mochi     Morning walk         🚶 walk        🔴 HIGH      30 min      Included: high priority, fits in remaining 65 min
✅ OK      Whiskers  Litter box cleaning  🧼 grooming    🟡 MEDIUM    10 min      Included: medium priority, fits in remaining 35 min
⏭️  SKIP  Whiskers  Weekly grooming      🧼 grooming    🟡 MEDIUM    30 min      Skipped: needs 30 min, only 25 min remaining
✅ OK      Whiskers  Brushing             🧼 grooming    🟢 LOW       15 min      Included: low priority, fits in remaining 25 min
⏭️  SKIP  Mochi     Fetch in the yard    🎾 enrichment  🟢 LOW       40 min      Skipped: needs 40 min, only 10 min remaining
```

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 29 tests) covers:

- **Core behaviors**: marking a task complete, adding a task to a pet
- **Sorting**: tasks are returned in chronological order by `scheduled_time`, including the empty-list edge case
- **Priority scheduling**: tasks are ordered by priority first (high → medium → low), ties within the same priority are broken by `scheduled_time`, and the empty-list edge case
- **Recurrence**: completing a `"daily"` task creates a next-day occurrence; a non-recurring task creates nothing
- **Conflict detection**: two tasks at the same `due_date` + `scheduled_time` are flagged, tasks at the same time on *different* dates are not, and no-conflict cases return an empty list
- **Filtering**: filtering `(pet, task)` pairs by pet name and/or completion status, including a no-match edge case
- **Plan generation**: tasks that don't fit the owner's available time are skipped, completed tasks are excluded, and an owner with no pets produces an empty plan
- **Next available slot**: finds the gap between two tasks, returns `None` when the day is fully booked, and ignores completed tasks when checking for conflicts
- **Persistence**: saving and reloading an owner (with pets, tasks, and a completed task) round-trips correctly, loading a missing file raises `FileNotFoundError`, and an owner with no pets saves/loads cleanly
- **Weekly rescheduling**: a non-recurring task returns `None`, an occurrence with no conflict keeps its original time, a conflicting occurrence is nudged to a different slot the same day, a fully-booked day advances to the next day, and exhausting the search window returns `None`

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 29 items

tests/test_pawpal.py::test_task_mark_complete_changes_status PASSED      [  3%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  6%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 10%]
tests/test_pawpal.py::test_sort_by_time_handles_empty_list PASSED        [ 13%]
tests/test_pawpal.py::test_sort_by_priority_then_time_orders_by_priority_first PASSED [ 17%]
tests/test_pawpal.py::test_sort_by_priority_then_time_breaks_ties_by_time PASSED [ 20%]
tests/test_pawpal.py::test_sort_by_priority_then_time_handles_empty_list PASSED [ 24%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 27%]
tests/test_pawpal.py::test_completing_task_with_no_recurrence_creates_nothing PASSED [ 31%]
tests/test_pawpal.py::test_detect_conflicts_flags_tasks_at_same_date_and_time PASSED [ 34%]
tests/test_pawpal.py::test_detect_conflicts_ignores_same_time_on_different_dates PASSED [ 37%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_list_when_no_overlaps PASSED [ 41%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 44%]
tests/test_pawpal.py::test_filter_tasks_by_completed_status PASSED       [ 48%]
tests/test_pawpal.py::test_filter_tasks_with_no_matching_pet_returns_empty_list PASSED [ 51%]
tests/test_pawpal.py::test_generate_plan_skips_tasks_that_dont_fit_available_time PASSED [ 55%]
tests/test_pawpal.py::test_generate_plan_excludes_already_completed_tasks PASSED [ 58%]
tests/test_pawpal.py::test_generate_plan_handles_owner_with_no_pets PASSED [ 62%]
tests/test_pawpal.py::test_find_next_available_slot_returns_gap_between_tasks PASSED [ 65%]
tests/test_pawpal.py::test_find_next_available_slot_returns_none_when_day_is_full PASSED [ 68%]
tests/test_pawpal.py::test_find_next_available_slot_ignores_completed_tasks PASSED [ 72%]
tests/test_pawpal.py::test_save_and_load_json_round_trip PASSED          [ 75%]
tests/test_pawpal.py::test_load_from_json_missing_file_raises PASSED     [ 79%]
tests/test_pawpal.py::test_save_to_json_handles_owner_with_no_pets PASSED [ 82%]
tests/test_pawpal.py::test_reschedule_weekly_task_returns_none_for_non_recurring_task PASSED [ 86%]
tests/test_pawpal.py::test_reschedule_weekly_task_keeps_original_time_when_no_conflict PASSED [ 89%]
tests/test_pawpal.py::test_reschedule_weekly_task_finds_a_different_slot_when_next_occurrence_conflicts PASSED [ 93%]
tests/test_pawpal.py::test_reschedule_weekly_task_advances_to_next_day_when_day_is_fully_booked PASSED [ 96%]
tests/test_pawpal.py::test_reschedule_weekly_task_returns_none_when_no_slot_found_in_window PASSED [100%]

============================= 29 passed in 0.14s ===============================
```

**Confidence Level:** 4/5

All core scheduling behaviors — sorting, priority-based scheduling, recurrence, conflict detection, filtering, plan generation, next-available-slot lookup, JSON persistence, and weekly rescheduling — are covered with both happy-path and edge-case tests, and all 29 pass. One star held back because `detect_conflicts()` only catches exact-time collisions, not partial/overlapping-duration conflicts (documented as a known limitation in `reflection.md`), so it isn't yet a fully reliable conflict guard for real-world scheduling.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks earliest-to-latest by their `scheduled_time` ("HH:MM") string. |
| Priority-based scheduling *(optional extension)* | `Scheduler.sort_by_priority_then_time()` | Sorts *all* tasks (not just pending ones) by priority first (high → medium → low), breaking ties within the same priority by `scheduled_time`. See [Priority-Based Scheduling](#optional-extension-priority-based-scheduling) below. |
| Priority/time-budget scheduling | `Scheduler.generate_plan()` | Sorts pending tasks by priority (ties broken by shorter duration first) and greedily fills the owner's `available_minutes`, skipping tasks that don't fit. |
| Filtering | `Scheduler.filter_tasks()` | Filters `(pet, task)` pairs by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks that share the same `due_date` + `scheduled_time` as a warning message; does not detect partial/overlapping-duration conflicts (see `reflection.md` 2b for why). |
| Recurring tasks | `Task.get_next_occurrence()`, `Pet.complete_task()` | Completing a "daily"/"weekly" task automatically creates its next occurrence, with `due_date` advanced via `datetime.timedelta`. |
| Next available slot *(optional extension)* | `Scheduler.find_next_available_slot()` | Converts every task's `scheduled_time` to minutes-since-midnight, walks the gaps between them (and before the first / after the last), and returns the earliest "HH:MM" gap that's at least as long as the requested duration, or `None` if the day (bounded by `day_start`/`day_end`) has no room left. Ignores completed tasks. |
| Data persistence *(optional extension)* | `Owner.save_to_json()`, `Owner.load_from_json()` | Serializes the full owner → pets → tasks tree to `data.json` and rebuilds it on load, so pets and tasks survive between app runs. See [Data Persistence](#data-persistence) below. |
| Weekly task rescheduling *(optional extension)* | `Scheduler.reschedule_weekly_task()` | Computes a recurring task's next occurrence; if that exact time overlaps another task's duration, reuses `find_next_available_slot()` to find an open gap the same day, or advances day-by-day (up to `max_extra_days`) if the day is full. See [Weekly Task Rescheduling](#optional-extension-weekly-task-rescheduling) below. |

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
- **Professional formatting** *(optional extension)*: tasks are tagged with a category emoji (🚶 walk,
  🍖 feeding, 💊 meds, 🎾 enrichment, 🧼 grooming) and a color-coded priority indicator (🔴 HIGH, 🟡 MEDIUM,
  🟢 LOW), and a ✅/⬜ shows completion status at a glance

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

Status    Pet       Task                 Category      Priority    Duration    Reason
--------  --------  -------------------  ------------  ----------  ----------  ---------------------------------------------------
✅ OK      Mochi     Evening meds         💊 meds        🔴 HIGH      5 min       Included: high priority, fits in remaining 90 min
✅ OK      Mochi     Breakfast            🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 85 min
✅ OK      Whiskers  Feeding              🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 75 min
✅ OK      Mochi     Morning walk         🚶 walk        🔴 HIGH      30 min      Included: high priority, fits in remaining 65 min
✅ OK      Whiskers  Litter box cleaning  🧼 grooming    🟡 MEDIUM    10 min      Included: medium priority, fits in remaining 35 min
⏭️  SKIP  Whiskers  Weekly grooming      🧼 grooming    🟡 MEDIUM    30 min      Skipped: needs 30 min, only 25 min remaining
✅ OK      Whiskers  Brushing             🧼 grooming    🟢 LOW       15 min      Included: low priority, fits in remaining 25 min
⏭️  SKIP  Mochi     Fetch in the yard    🎾 enrichment  🟢 LOW       40 min      Skipped: needs 40 min, only 10 min remaining

All tasks sorted by scheduled time:

Time    Task                 Category      Priority
------  -------------------  ------------  ----------
08:00   Morning walk         🚶 walk        🔴 HIGH
08:15   Feeding              🍖 feeding     🔴 HIGH
08:30   Breakfast            🍖 feeding     🔴 HIGH
10:00   Weekly grooming      🧼 grooming    🟡 MEDIUM
12:00   Litter box cleaning  🧼 grooming    🟡 MEDIUM
17:00   Fetch in the yard    🎾 enrichment  🟢 LOW
19:30   Evening meds         💊 meds        🔴 HIGH
20:00   Brushing             🧼 grooming    🟢 LOW

All tasks sorted by priority, then by time:

Priority    Time    Task                 Category
----------  ------  -------------------  ------------
🔴 HIGH      08:00   Morning walk         🚶 walk
🔴 HIGH      08:15   Feeding              🍖 feeding
🔴 HIGH      08:30   Breakfast            🍖 feeding
🔴 HIGH      19:30   Evening meds         💊 meds
🟡 MEDIUM    10:00   Weekly grooming      🧼 grooming
🟡 MEDIUM    12:00   Litter box cleaning  🧼 grooming
🟢 LOW       17:00   Fetch in the yard    🎾 enrichment
🟢 LOW       20:00   Brushing             🧼 grooming

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
Whiskers: Weekly grooming

Completing 'Morning walk' (due 2026-07-14, frequency=daily)
✅ Completed: True
🔁 Next occurrence created for 2026-07-15 (completed=False)

Checking for scheduling conflicts:

⚠️  Conflict on 2026-07-14 at 08:30: Mochi's 'Breakfast', Whiskers's 'Play session'

Finding next available 20-minute slot for Mochi today:

🕒 Next available slot: 08:45

Rescheduling 'Weekly grooming' for next week (conflicts with a vet checkup at 10:15):

🔁 Moved to 2026-07-21 at 08:00 (originally 10:00).

💾 Saved Jordan's data to demo_data.json.
💾 Reloaded owner 'Jordan' with 2 pets and 11 total tasks.
```

## Optional Extension: Priority-Based Scheduling

`Task` already carries a `priority` field (`"low"`, `"medium"`, or `"high"`); this extension adds a second
sorting algorithm — `Scheduler.sort_by_priority_then_time(tasks)` — that goes beyond simple chronological
sorting: it sorts by priority first, and only falls back to `scheduled_time` to break ties *within* the same
priority level. This is different from `generate_plan()`, which sorts *pending* tasks by priority (ties
broken by shortest duration) in order to greedily fill the owner's available minutes — the new method sorts
*every* task (pending or completed) purely for display, with time as the tiebreaker instead of duration.

**How it works:** tasks are sorted with a compound key — `(PRIORITY_ORDER[task.priority], task.scheduled_time)`
— where `PRIORITY_ORDER` maps `"high"` → 0, `"medium"` → 1, `"low"` → 2, so high-priority tasks always sort
before medium and low regardless of what time they're scheduled, and same-priority tasks fall back to
chronological order.

**Files modified:** `pawpal_system.py` (new `Scheduler.sort_by_priority_then_time` method), `main.py` (CLI
demo), `app.py` ("All Tasks — Sorted by Priority, then Time" table), `tests/test_pawpal.py` (3 new tests).

**CLI output example** — given the same tasks as the "sorted by time" demo above, but now grouped by
priority first:

```
All tasks sorted by scheduled time:

Time    Task                 Category      Priority
------  -------------------  ------------  ----------
08:00   Morning walk         🚶 walk        🔴 HIGH
08:15   Feeding              🍖 feeding     🔴 HIGH
08:30   Breakfast            🍖 feeding     🔴 HIGH
10:00   Weekly grooming      🧼 grooming    🟡 MEDIUM
12:00   Litter box cleaning  🧼 grooming    🟡 MEDIUM
17:00   Fetch in the yard    🎾 enrichment  🟢 LOW
19:30   Evening meds         💊 meds        🔴 HIGH
20:00   Brushing             🧼 grooming    🟢 LOW

All tasks sorted by priority, then by time:

Priority    Time    Task                 Category
----------  ------  -------------------  ------------
🔴 HIGH      08:00   Morning walk         🚶 walk
🔴 HIGH      08:15   Feeding              🍖 feeding
🔴 HIGH      08:30   Breakfast            🍖 feeding
🔴 HIGH      19:30   Evening meds         💊 meds
🟡 MEDIUM    10:00   Weekly grooming      🧼 grooming
🟡 MEDIUM    12:00   Litter box cleaning  🧼 grooming
🟢 LOW       17:00   Fetch in the yard    🎾 enrichment
🟢 LOW       20:00   Brushing             🧼 grooming
```

Notice how "Evening meds" (19:30, high priority) moves up above "Litter box cleaning" (12:00, medium
priority) — pure time-sorting would put it last, but priority-based sorting keeps all four high-priority
tasks together first, still ordered chronologically among themselves. (The emoji/tabulate formatting shown
here is from the [Professional UI and Output Formatting](#optional-extension-professional-ui-and-output-formatting)
extension below — the sorting logic itself doesn't require it.)

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

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

## Optional Extension: Professional UI and Output Formatting

Raw text output is hard to scan — this extension adds category emojis, color-coded priority indicators, and
completion checkmarks throughout both the CLI (`main.py`) and the Streamlit UI (`app.py`), plus structured
tables in the CLI via the [`tabulate`](https://pypi.org/project/tabulate/) library.

**Functions/libraries used:**

- **`formatting.py`** *(new module)* — a small presentation-only helper module, kept separate from
  `pawpal_system.py` so the logic layer stays free of display concerns:
  - `CATEGORY_EMOJIS` maps each task category to an emoji: 🚶 walk, 🍖 feeding, 💊 meds, 🎾 enrichment,
    🧼 grooming (falls back to 📋 for anything else).
  - `PRIORITY_INDICATORS` maps each priority to a color-coded dot + label: 🔴 HIGH, 🟡 MEDIUM, 🟢 LOW.
  - `category_label(category)`, `priority_label(priority)`, and `status_emoji(completed)` are the functions
    both `main.py` and `app.py` call to render these consistently.
- **`tabulate`** *(new dependency, added to `requirements.txt`)* — used in `main.py` to render the daily
  schedule and both sorted-task listings as aligned CLI tables instead of one-line-per-task prints.
- **Streamlit's built-in color coding** — `st.success()` (green) / `st.warning()` (yellow) were already used
  for included vs. skipped plan items and conflict warnings; this extension layers emoji on top (✅/⏭️/⚠️/🕒/💾)
  and adds a category selectbox to the "Add task" form so every task actually gets a matching emoji instead
  of always being `"general"`.

**Files modified:** `formatting.py` (new), `main.py` (tabulate tables + emoji prefixes throughout),
`app.py` (emoji/priority labels in all task tables and messages, category selectbox added to the task form),
`requirements.txt` (added `tabulate>=0.9`).

**CLI output example** — the same "Today's Schedule" demo as above, now genuinely reflects what running
`python main.py` prints (color/emoji indicators plus an aligned `tabulate` table):

```
Today's Schedule for Jordan (90 min available):

Status    Pet       Task                 Category      Priority    Duration    Reason
--------  --------  -------------------  ------------  ----------  ----------  ---------------------------------------------------
✅ OK      Mochi     Evening meds         💊 meds        🔴 HIGH      5 min       Included: high priority, fits in remaining 90 min
✅ OK      Mochi     Breakfast            🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 85 min
✅ OK      Whiskers  Feeding              🍖 feeding     🔴 HIGH      10 min      Included: high priority, fits in remaining 75 min
✅ OK      Mochi     Morning walk         🚶 walk        🔴 HIGH      30 min      Included: high priority, fits in remaining 65 min
✅ OK      Whiskers  Litter box cleaning  🧼 grooming    🟡 MEDIUM    10 min      Included: medium priority, fits in remaining 35 min
⏭️  SKIP  Whiskers  Weekly grooming      🧼 grooming    🟡 MEDIUM    30 min      Skipped: needs 30 min, only 25 min remaining
✅ OK      Whiskers  Brushing             🧼 grooming    🟢 LOW       15 min      Included: low priority, fits in remaining 25 min
⏭️  SKIP  Mochi     Fetch in the yard    🎾 enrichment  🟢 LOW       40 min      Skipped: needs 40 min, only 10 min remaining
```

**Note on Windows terminals:** the default Windows console codepage (cp1252) can't encode emoji, so `main.py`
reconfigures `sys.stdout` to UTF-8 at startup if it isn't already — without that, printing any of the tables
above raises a `UnicodeEncodeError`.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Optional Extension: Weekly Task Rescheduling

A `"weekly"` task's built-in recurrence (`Task.get_next_occurrence()`) just advances `due_date` by exactly 7
days at the same `scheduled_time` — it has no idea whether that slot is still free next week. This extension
adds `Scheduler.reschedule_weekly_task(owner, task, max_extra_days=7)`, which nudges the next occurrence
forward only as far as needed to avoid a real conflict.

**How it works:**

1. Compute the task's normal next occurrence (`task.get_next_occurrence()`). If the task doesn't recur,
   return `None`.
2. Check whether that exact time slot overlaps another task's duration on the same day (a duration-aware
   overlap check — two tasks conflict if their `[start, start + duration)` ranges intersect, not just if
   they share an identical start time). If there's no overlap, keep the original time and return.
3. If there is a conflict, reuse `find_next_available_slot()` to search that same day for an open gap long
   enough for the task. If one exists, move the task to that time (same day).
4. If the day is fully booked, advance to the next day and repeat steps 2–3, up to `max_extra_days` (default
   7) days ahead. If no slot is found within that window, return `None`.

**Known limitation:** when a conflict does push the task to a different time, the replacement is the
*earliest* open gap that day (from `find_next_available_slot()`), not necessarily the time closest to the
task's original `scheduled_time` — see the [Prompt Comparison](ai_interactions.md) writeup in
`ai_interactions.md` for how this trade-off was decided.

**Files modified:** `pawpal_system.py` (extracted `_time_to_minutes`/`_minutes_to_time` helpers used by both
`find_next_available_slot` and the new method; added `Scheduler.reschedule_weekly_task`), `main.py` (CLI
demo), `tests/test_pawpal.py` (5 new tests), `ai_interactions.md` (Prompt Comparison section for Challenge 5).

**CLI output example** — Whiskers has a `"weekly"` "Weekly grooming" task at 10:00; next week a "Vet checkup"
is already booked 10:15–10:35, which overlaps it:

```
Rescheduling 'Weekly grooming' for next week (conflicts with a vet checkup at 10:15):

🔁 Moved to 2026-07-21 at 08:00 (originally 10:00).
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
