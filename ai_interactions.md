# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a third algorithmic capability to PawPal+ beyond the base requirements (sorting, filtering, conflict
detection, plan generation): a "next available slot" finder that, given a pet's day and a duration, returns
the earliest open time gap long enough for a new task. Asked the agent to wire it into both the CLI demo and
the Streamlit UI, add tests, and update the README.

**What did the agent do?**

- Added `Scheduler.find_next_available_slot()` to `pawpal_system.py` — converts task times to
  minutes-since-midnight, sorts by `scheduled_time`, walks the gaps between tasks (and before the first /
  after the last, bounded by configurable `day_start`/`day_end`), and returns the first "HH:MM" gap that fits
  the requested duration, or `None` if nothing fits.
- Added a CLI demo block to `main.py` that calls the new method against Mochi's existing tasks and prints the
  result.
- Added a "Find Next Available Slot" section to `app.py` (duration input + button, using `st.success`/
  `st.warning` to display the result), and added `date` to the existing `datetime` import.
- Added 3 new tests to `tests/test_pawpal.py`: a gap between two tasks, a fully-booked day returning `None`,
  and confirming completed tasks are ignored when computing gaps.
- Ran the full suite (`python -m pytest`) — all 18 tests passed.
- Updated `README.md`: added the feature to the feature list, the "Smarter Scheduling" table, the test-count
  callouts (15 → 18), and a new "Optional Extension" section with sample CLI output for both the found-a-slot
  and no-slot-available cases.

**What did you have to verify or fix manually?**

Ran `main.py` directly to confirm the printed slot (`08:45`) actually matched the gap between Mochi's Morning
walk (08:00–08:30) and Breakfast (08:30–08:40, at 10 min duration) — the arithmetic checked out on first try,
so no logic changes were needed. Double-checked the `app.py` edit didn't leave a redundant local `datetime`
import after moving `date` to the top-level import.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

Note: I didn't have a second AI service (e.g. Gemini/ChatGPT) available in this environment, so instead of
"Claude vs. another model" I compared **two different prompting strategies given to the same model (Claude
Sonnet 5)** on the same complex algorithmic task — the template explicitly allows "two different prompts (or
two different models)". Task: *rescheduling a weekly recurring task so it doesn't collide with an existing
task, without just blindly advancing the due_date by 7 days.*

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Sonnet 5 | Claude Sonnet 5 |
| **Prompt** | "Write a simple greedy algorithm for rescheduling a missed/conflicting weekly task: advance the due_date by 7 days, and if that exact time is already taken by another task, push forward day-by-day until you find a day with no task at that same time." | "Design a more robust rescheduling algorithm that reuses the existing `find_next_available_slot()` method: advance by 7 days as a baseline, then check for conflicts and fall back to searching for an open slot on that day (or later days) if needed." |
| **Response summary** | A self-contained loop that computes `due_date + 7 days`, then for each extra day checks whether *any* existing task starts at the *exact same* `scheduled_time`; the first day with no exact-time match wins. | A loop that reuses `find_next_available_slot()`: for each candidate day, if the original time slot is free it's kept, otherwise `find_next_available_slot()` is called to find the earliest open gap of the right duration that day, advancing to the next day if the day is fully booked. |
| **What was useful** | Very short and easy to read; no dependency on other Scheduler methods. | Reuses already-tested conflict logic instead of re-deriving it; correctly treats conflicts as *duration overlaps* (not just identical start times), and degrades gracefully (day fully booked → try the next day) using code that already existed and was already unit-tested. |
| **Problems noticed** | The "exact same start time" check is wrong: two tasks with *different* start times can still overlap in duration (e.g. an existing 10:15–10:35 task doesn't collide by this check with a new 10:00 task, even though they overlap 10:15–10:30). It also duplicates conflict-detection logic that already exists elsewhere in the codebase. | Left unchecked, an early draft always called `find_next_available_slot()` even when the original time was actually free, silently moving tasks that didn't need to move. Needed an explicit "is the original slot actually free?" check first, added before falling back to the slot search. |
| **Decision** | Not used as-is — its conflict check was a real correctness bug (silently misses overlapping tasks with staggered start times). | Used, after fixing the "always searches even when unnecessary" issue: the task's original scheduled_time is checked directly (open-interval overlap, so it's duration-aware, not just start-time-aware) before ever calling `find_next_available_slot()`, and searching only happens as a genuine fallback. |

**Which approach did you use in your final implementation and why?**

A refined version of Option B, implemented as `Scheduler.reschedule_weekly_task()` in `pawpal_system.py`. I
kept Option B's core idea — reuse `find_next_available_slot()` as the fallback search instead of reinventing
conflict detection — but fixed its "always searches" bug by adding an explicit duration-aware overlap check
first (borrowing the *intent* of Option A's per-day loop, but checking real time-range overlap instead of
exact-start-time equality, which was Option A's actual flaw). This kept the final method both correct
(duration-aware conflicts) and DRY (no duplicate slot-finding logic). One known trade-off, documented in the
method's docstring: when a conflict does push the task to a new day, the replacement time is the *earliest*
open gap that day, not necessarily the time closest to the task's original `scheduled_time` — acceptable for
this project's scope, but worth flagging as a limitation, the same way `detect_conflicts()`'s exact-time-only
matching is flagged elsewhere in `reflection.md`.
