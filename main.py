"""Manual demo script for verifying PawPal+ scheduling logic in the terminal."""

from pawpal_system import Task, Pet, Owner, Scheduler

# Owner has 90 minutes available today — enough to fit some tasks, not all.
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
mochi.add_task(Task("Morning walk", 30, "high", "walk"))
mochi.add_task(Task("Breakfast", 10, "high", "feeding"))
mochi.add_task(Task("Evening meds", 5, "high", "meds"))
mochi.add_task(Task("Fetch in the yard", 40, "low", "enrichment"))

whiskers = Pet(name="Whiskers", species="cat")
whiskers.add_task(Task("Litter box cleaning", 10, "medium", "grooming"))
whiskers.add_task(Task("Feeding", 10, "high", "feeding"))
whiskers.add_task(Task("Brushing", 15, "low", "grooming"))

owner.add_pet(mochi)
owner.add_pet(whiskers)

scheduler = Scheduler()
plan = scheduler.generate_plan(owner)

print(f"Today's Schedule for {owner.name} ({owner.available_minutes} min available):\n")
for item in plan:
    status = "OK" if item.included else "SKIP"
    print(f"[{status}] {item.pet_name}: {item.task.title} ({item.task.duration_minutes} min) - {item.reason}")
