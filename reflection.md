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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
