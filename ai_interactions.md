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

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
