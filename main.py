"""Manual demo script for verifying PawPal+ scheduling logic in the terminal."""

from pawpal_system import Task, Pet, Owner, Scheduler

# Owner has 90 minutes available today — enough to fit some tasks, not all.
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
mochi.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"))
mochi.add_task(Task("Evening meds", 5, "high", "meds", scheduled_time="19:30"))
mochi.add_task(Task("Breakfast", 10, "high", "feeding", scheduled_time="08:30"))
mochi.add_task(Task("Fetch in the yard", 40, "low", "enrichment", scheduled_time="17:00"))

whiskers = Pet(name="Whiskers", species="cat")
whiskers.add_task(Task("Brushing", 15, "low", "grooming", scheduled_time="20:00"))
whiskers.add_task(Task("Feeding", 10, "high", "feeding", scheduled_time="08:15"))
whiskers.add_task(Task("Litter box cleaning", 10, "medium", "grooming", scheduled_time="12:00"))

owner.add_pet(mochi)
owner.add_pet(whiskers)

scheduler = Scheduler()
plan = scheduler.generate_plan(owner)

print(f"Today's Schedule for {owner.name} ({owner.available_minutes} min available):\n")
for item in plan:
    status = "OK" if item.included else "SKIP"
    print(f"[{status}] {item.pet_name}: {item.task.title} ({item.task.duration_minutes} min) - {item.reason}")

# --- Sorting demo: tasks were added out of order above; sort_by_time fixes that. ---
all_tasks = [task for _, task in owner.get_all_tasks()]
print("\nAll tasks sorted by scheduled time:\n")
for task in scheduler.sort_by_time(all_tasks):
    print(f"{task.scheduled_time} - {task.title}")

# --- Filtering demo: only Mochi's tasks, then only incomplete tasks. ---
print("\nFiltered: Mochi's tasks only:\n")
for pet, task in scheduler.filter_tasks(owner.get_all_tasks(), pet_name="Mochi"):
    print(f"{pet.name}: {task.title}")

print("\nFiltered: incomplete tasks only:\n")
for pet, task in scheduler.filter_tasks(owner.get_all_tasks(), completed=False):
    print(f"{pet.name}: {task.title}")

# --- Recurring task demo: completing a daily task should spawn tomorrow's occurrence. ---
morning_walk = next(t for t in mochi.tasks if t.title == "Morning walk")
print(f"\nCompleting '{morning_walk.title}' (due {morning_walk.due_date}, frequency={morning_walk.frequency})")
next_occurrence = mochi.complete_task(morning_walk)
print(f"Completed: {morning_walk.completed}")
print(f"Next occurrence created for {next_occurrence.due_date} (completed={next_occurrence.completed})")

# --- Conflict detection demo: two tasks (different pets) scheduled at the same time. ---
whiskers.add_task(Task("Play session", 15, "medium", "enrichment", scheduled_time="08:30"))

print("\nChecking for scheduling conflicts:\n")
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    for warning in conflicts:
        print(f"WARNING: {warning}")
else:
    print("No conflicts found.")
