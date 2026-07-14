# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Thee Core user actions identified before designing classes:**

- **Add or edit a pet care task**
  - What it means: the owner enters a task like a walk, feeding, medication, grooming, or enrichment activity.
  - Why it's one action, not five: every task type needs the same basic info — a title, how long it takes, and how important it is. Instead of building separate logic for "walks" vs "feedings," one generic `Task` idea handles all of them, with a `category` field to tell them apart.

- **Set up the pet/owner profile and constraints**
  - What it means: the owner records basic pet info (name, species) and the constraints for the day — mainly, how much time they actually have available.
  - Why it matters for design: the scheduler can't make good decisions in a vacuum. It needs to know the ceiling (available minutes) before it can decide what fits and what gets cut.

- **Generate today's plan**
  - What it means: the owner clicks one button, and the system looks at all entered tasks plus the constraints, then produces an ordered schedule — and explains _why_ each task made the cut (or didn't).
  - Why it's the most important action: this is the one action that runs real logic instead of just storing data. It's also why the design needs to track _reasoning_, not just a final list — the scenario explicitly asks the assistant to explain its choices, not just spit out a schedule.

**Why these three actions shaped the class design:**

I used these actions as a checklist for what classes and methods I'd need. Each action pointed to a different responsibility:

- Action 1 → needs a `Task`-like class that can represent any care activity generically.
- Action 2 → needs a `Pet` (and possibly `Owner`) class to hold profile info, plus somewhere to store the day's time constraint.
- Action 3 → needs a scheduler/planner responsible for selecting and ordering tasks, and for recording _why_ it made each decision — not something a simple list could do on its own.

Thinking about actions before classes helped avoid a common mistake: designing a `Task` class that only stores data, then bolting scheduling logic onto it later as an afterthought. Instead, the need to "explain the plan" was baked in from the start.

**Building blocks (Step 2):**

- **Owner** — the person using the app
  - Attributes: `name`, `available_minutes` (how much time they have today), `preferences` (e.g., preferred start time)
  - Methods: none — it's just a data holder that other parts of the system read from.

- **Pet** — the animal being cared for (one pet per owner, kept simple for now)
  - Attributes: `name`, `species`, `tasks` (a list of `Task` objects belonging to this pet)
  - Methods: `add_task(task)` — a small convenience method to append a new task to its own list.

- **Task** — one pet care activity (walk, feeding, meds, enrichment, grooming)
  - Attributes: `title`, `duration_minutes`, `priority` (low/medium/high), `category`
  - Methods: none — just a data holder describing itself.

- **Planner** — the scheduling logic, the "brain" of the app
  - Attributes: operates on a `Pet`'s tasks and the `Owner`'s `available_minutes` when called, rather than storing much of its own state.
  - Methods:
    - `generate_plan(pet, owner)` — sorts tasks by priority, adds tasks while time remains, skips ones that don't fit.
    - reasoning built into the plan output — for each task, records why it was included or skipped.

Most classes here (`Owner`, `Pet`, `Task`) are simple data holders with barely any methods — all the real thinking happens in one place, `Planner`. This keeps the design easy to reason about and easy to test.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After drafting the skeleton in `pawpal_system.py`, I reviewed it with AI assistance and made two changes:

1. **Added a `pet` field to `Owner`.** The original skeleton had `Owner` and `Pet` as two disconnected dataclasses — the UML diagram showed an "Owner has Pet" relationship, but nothing in the code actually enforced it. Anyone constructing these objects had to remember to keep a matching `Owner`/`Pet` pair by convention, which is fragile. Adding `pet: Pet` onto `Owner` makes the relationship structural instead of implied.

2. **Added a `PlannedItem` dataclass and changed `generate_plan()`'s return type from `list` to `List[PlannedItem]`.** The original skeleton had no place to store *why* a task was included or skipped, even though explaining the plan is a core requirement from the scenario. Returning a plain list of `Task` objects would have meant either bolting reasoning on later (e.g., a parallel list of strings, easy to get out of sync) or building a separate `explain_plan()` method that has to re-derive reasoning after the fact. Instead, `PlannedItem` pairs each `Task` with `included: bool` and `reason: str` directly, so the explanation is generated at the same time as the decision and can't drift out of sync with it.

**Later change: switching from one pet per owner to multiple pets per owner, and renaming `Planner` to `Scheduler`.**

When implementing the full scheduling logic (moving from stubs to real behavior), the assignment's spec for this step explicitly described `Owner` as managing *multiple* pets and a class named `Scheduler`, which conflicted with the simpler one-pet design from earlier. I chose to align with that fuller spec rather than keep the simplified version, which required several concrete changes:

- **`Owner.pet: Pet` → `Owner.pets: List[Pet]`.** A single `pet` field can't represent a busy owner with more than one animal, which the scenario language ("their pet(s)") always implied was in scope. I also added `add_pet()` so pets can be added incrementally, matching how tasks are added to a pet one at a time.

- **Added `Owner.get_all_tasks()`.** With multiple pets, something needs to flatten each pet's task list into one combined list before scheduling can happen. I put this method on `Owner` rather than on `Scheduler`, because `Owner` already has direct access to its own `pets` — this keeps `Scheduler` from needing to know about `Owner`'s internal structure (it just calls `owner.get_all_tasks()` and gets back everything, an example of encapsulation: each class manages its own internal data and exposes a simple method for others to use).

- **`Planner` renamed to `Scheduler`, and its method signature changed from `generate_plan(pet, owner)` to `generate_plan(owner)`.** Once an owner can have multiple pets, it no longer makes sense for the caller to hand in one specific `pet` — the scheduler needs to retrieve tasks *across all* of the owner's pets itself, via `get_all_tasks()`, rather than being handed a single pet's task list.

- **`PlannedItem` gained a `pet_name` field.** With only one pet, saying "this task was included" was unambiguous. With multiple pets, the explanation needs to say *whose* task it is (e.g., "Mochi's walk was included..."), so each `PlannedItem` now records which pet the task belongs to.

- **`Task` gained `frequency` and `completed` fields**, and the scheduler now filters out tasks where `completed` is already `True` before scheduling — there's no reason to plan time for something already done today.

This is a good example of a design changing mid-implementation for a legitimate reason (a clearer/fuller spec surfaced partway through), rather than scope creep — but it did mean revisiting decisions (one pet, `Planner` naming) that had already been written up earlier in this section, which is worth noting as a lesson in itself: locking in a "simple first" design too early can mean rework later if the fuller requirements were knowable from the start.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers four constraints: the owner's `available_minutes` (a hard time budget), each task's `priority` (high/medium/low, the ordering signal), `completed` status (finished tasks are excluded from today's plan), and `scheduled_time` + `due_date` together (used for sorting and conflict detection, not for the plan itself).

Time and priority mattered most because they map directly to the scenario: a busy owner has a fixed amount of time and needs the *most important* care tasks (meds, feeding) done first if everything can't fit. `generate_plan()` treats time as a hard ceiling — it's structurally enforced by decrementing `remaining_minutes` and refusing to include a task that doesn't fit — while priority is a soft ordering signal (ties broken by shorter duration, so more low-priority tasks can still squeeze in if time remains). `scheduled_time` and `due_date` were added later, once sorting and conflict detection were in scope, but they intentionally don't affect *which* tasks get chosen in `generate_plan()` — only priority and duration do — to keep the two concerns (what to include vs. when it happens) separate.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff: `Scheduler.detect_conflicts()` only checks for exact scheduled_time matches, not overlapping durations.**

Two tasks are only flagged as a conflict if they share the exact same `(due_date, scheduled_time)` slot. A 30-minute task starting at 08:00 and a separate task starting at 08:15 would genuinely overlap in real life, but my scheduler won't catch that — it only compares start times, not start-time-plus-duration ranges.

I chose this simplification deliberately rather than by accident. Real interval-overlap checking requires comparing every pair of tasks' `[start, start + duration]` ranges against each other, which is more code and a more expensive check (checking all pairs instead of grouping by a single key). For a busy pet owner with a handful of daily tasks, exact-time conflicts (e.g., accidentally scheduling two things at 8:00 AM) are the more common and more obviously avoidable mistake, while partial-overlap conflicts are a subtler edge case. Catching the common case with a simple, fast, easy-to-read implementation seemed like the right scope for this project, with full interval-overlap detection noted as a reasonable improvement for a future iteration rather than something this version needed to handle.

I verified this method with AI assistance by running the actual demo script (`main.py`) rather than just reading the code — that surfaced a real bug where a recurring task's next-day occurrence was being flagged as conflicting with itself, because the first version of this method grouped only by `scheduled_time` and ignored `due_date` entirely. Running it, not just reading it, is what caught that.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant across the full lifecycle: brainstorming the initial UML from user actions (Phase 1), drafting the algorithm implementations for sorting/filtering/recurrence/conflict detection (Phase 4), generating the pytest suite (Phase 5), and wiring the Streamlit UI plus polishing docs (Phase 6). The most effective feature wasn't any single suggestion — it was the assistant actually *running* the code after writing it (`python main.py`, `pytest`) instead of just producing code and assuming it worked. That closed-loop pattern (write → run → read the real output → fix) caught bugs a code-only review would have missed.

The most useful prompts were the ones that asked for a *concrete edge case*, not a general review — e.g., "what happens if two tasks share the same time but different due_date?" produced a much more useful answer than "does this method look right?". Asking "why is this test failing — is the bug in my test or in `pawpal_system.py`?" (per the Phase 5 instructions) was also a good habit, since it forces an explicit diagnosis instead of a reflexive fix.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The clearest example is `Scheduler.detect_conflicts()` (see section 2b): the first implementation grouped tasks by `scheduled_time` alone. That looked correct on paper, but I didn't accept it purely from reading the code — I ran `main.py`'s recurrence demo, where completing a daily task creates a next-day occurrence at the *same* `scheduled_time`, and watched it get incorrectly flagged as conflicting with its own predecessor. That observed, wrong output was the evidence that the suggestion was incomplete; the fix (group by `(due_date, scheduled_time)` instead) came directly from diagnosing *why* the wrong output happened, not from a second guess. The lesson: for anything with real logic (not just boilerplate), I verify by executing it and inspecting actual output, not by trusting that plausible-looking code is correct.

Working across dedicated phases (planning → implementation → testing → docs, each revisited as its own step even within one continuous session) also helped keep this honest — treating "write the tests" and "run the tests" as separate, sequential steps rather than assuming a test that was written must pass.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 15-test suite in `tests/test_pawpal.py` covers the five algorithmic behaviors that make this scheduler "smart" rather than a plain to-do list: chronological sorting (`sort_by_time`), pet/status filtering (`filter_tasks`), daily recurrence (`get_next_occurrence`/`complete_task`), same-slot conflict detection (`detect_conflicts`), and priority/time-budget plan generation (`generate_plan`) — each with at least one happy-path case and one edge case (empty list, non-recurring task, no matching pet, zero available minutes, an owner with no pets).

These were the tests worth writing precisely because they're not obviously correct just by reading the code — they involve stateful mutation (`complete_task` both marks a task complete *and* creates a new one), grouping logic that's easy to get subtly wrong (as the conflict-detection bug showed), and greedy ordering that depends on tie-breaking rules. A pet owner would trust whatever the plan says; a silent bug in any of these would produce a wrong schedule that looks plausible.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'd rate my confidence at 4/5 stars, matching the README's testing section. All 15 tests pass, and the algorithms have been exercised both as unit tests and end-to-end through `main.py` and the Streamlit UI. The one star held back is for known, documented gaps rather than unknown ones: `detect_conflicts()` only catches exact-time collisions, not overlapping durations (a 30-minute task at 08:00 won't be flagged against one starting at 08:15).

With more time I'd test: overlapping-duration conflicts once that logic exists; `"weekly"` recurrence crossing a month or year boundary; a task whose `scheduled_time` is malformed (not zero-padded "HH:MM"), which would silently sort wrong since `sort_by_time` relies on string comparison; and multiple tasks tied on both priority *and* duration, to confirm the tie-break order is stable and doesn't depend on dict/list ordering quirks.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with catching the recurring-task conflict bug (section 2b/3b) by actually running the demo instead of stopping at a code read. It's a small bug, but it's exactly the kind of interaction-between-features bug (recurrence + conflict detection, two features built independently) that's easy to miss when each feature is tested in isolation, and it validated the whole "verify by running, not just reading" approach I used for the rest of the project.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd implement real interval-overlap conflict detection (comparing `[scheduled_time, scheduled_time + duration]` ranges, not just exact start-time matches) since that's the most concrete gap left between what the scheduler does and what a pet owner would actually need. I'd also extend `generate_plan()` beyond a single "today" plan to look ahead across the recurring tasks it generates, so the owner could see tomorrow's plan already accounting for today's completions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Being the "lead architect" meant the AI was fast at producing plausible-looking code and tests, but I was the one who had to define what "correct" meant (the acceptance criteria — e.g., "conflicts must consider due_date, not just time") and actually verify it by running things, not just accepting well-formatted output. The AI is very good at generating a first draft and even at explaining its own reasoning when asked, but it doesn't know what it doesn't know about the scenario's real-world implications (like same-time-different-date not being a real conflict) unless prompted to actually execute and check. That division of labor — AI for breadth and speed, me for judgment and verification — is what made the difference between code that looks right and code that is right.
