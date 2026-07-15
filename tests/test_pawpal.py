"""Quick tests for PawPal+ core classes."""

from datetime import date, timedelta

import pytest

from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high", "walk")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high", "feeding"))

    assert len(pet.tasks) == 1


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler()
    tasks = [
        Task("Evening meds", 5, "high", "meds", scheduled_time="19:30"),
        Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"),
        Task("Lunch", 10, "medium", "feeding", scheduled_time="12:00"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [t.title for t in sorted_tasks] == ["Morning walk", "Lunch", "Evening meds"]


def test_sort_by_time_handles_empty_list():
    scheduler = Scheduler()

    assert scheduler.sort_by_time([]) == []


def test_sort_by_priority_then_time_orders_by_priority_first():
    scheduler = Scheduler()
    tasks = [
        Task("Brushing", 15, "low", "grooming", scheduled_time="20:00"),
        Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"),
        Task("Litter box cleaning", 10, "medium", "grooming", scheduled_time="12:00"),
        Task("Evening meds", 5, "high", "meds", scheduled_time="19:30"),
    ]

    sorted_tasks = scheduler.sort_by_priority_then_time(tasks)

    # High priority tasks first (earliest time wins ties), then medium, then low.
    assert [t.title for t in sorted_tasks] == [
        "Morning walk",
        "Evening meds",
        "Litter box cleaning",
        "Brushing",
    ]


def test_sort_by_priority_then_time_breaks_ties_by_time():
    scheduler = Scheduler()
    tasks = [
        Task("Evening meds", 5, "high", "meds", scheduled_time="19:30"),
        Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"),
        Task("Breakfast", 10, "high", "feeding", scheduled_time="08:30"),
    ]

    sorted_tasks = scheduler.sort_by_priority_then_time(tasks)

    assert [t.title for t in sorted_tasks] == ["Morning walk", "Breakfast", "Evening meds"]


def test_sort_by_priority_then_time_handles_empty_list():
    scheduler = Scheduler()

    assert scheduler.sort_by_priority_then_time([]) == []


# --- Recurrence logic ---

def test_completing_daily_task_creates_next_day_occurrence():
    pet = Pet("Mochi", "dog")
    today = date(2026, 1, 1)
    task = Task("Morning walk", 30, "high", "walk", frequency="daily", due_date=today)
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.title == task.title
    assert next_task in pet.tasks


def test_completing_task_with_no_recurrence_creates_nothing():
    pet = Pet("Mochi", "dog")
    task = Task("One-time vet visit", 60, "high", "meds", frequency="once")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert task.completed is True
    assert next_task is None
    assert len(pet.tasks) == 1


# --- Conflict detection ---

def test_detect_conflicts_flags_tasks_at_same_date_and_time():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)

    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", scheduled_time="08:30", due_date=today))
    whiskers = Pet("Whiskers", "cat")
    whiskers.add_task(Task("Play session", 15, "medium", "enrichment", scheduled_time="08:30", due_date=today))

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    conflicts = scheduler.detect_conflicts(owner)

    assert len(conflicts) == 1
    assert "Mochi's 'Breakfast'" in conflicts[0]
    assert "Whiskers's 'Play session'" in conflicts[0]


def test_detect_conflicts_ignores_same_time_on_different_dates():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)
    tomorrow = today + timedelta(days=1)

    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00", due_date=today))
    mochi.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00", due_date=tomorrow))
    owner.add_pet(mochi)

    conflicts = scheduler.detect_conflicts(owner)

    assert conflicts == []


def test_detect_conflicts_returns_empty_list_when_no_overlaps():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"))
    pet.add_task(Task("Evening meds", 5, "high", "meds", scheduled_time="19:30"))
    owner.add_pet(pet)

    assert scheduler.detect_conflicts(owner) == []


# --- Filtering ---

def test_filter_tasks_by_pet_name():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", 30, "high", "walk"))
    whiskers = Pet("Whiskers", "cat")
    whiskers.add_task(Task("Brushing", 15, "low", "grooming"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    filtered = scheduler.filter_tasks(owner.get_all_tasks(), pet_name="Mochi")

    assert [task.title for _, task in filtered] == ["Morning walk"]


def test_filter_tasks_by_completed_status():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    pet = Pet("Mochi", "dog")
    done = Task("Morning walk", 30, "high", "walk")
    done.mark_complete()
    pending = Task("Evening meds", 5, "high", "meds")
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)

    incomplete = scheduler.filter_tasks(owner.get_all_tasks(), completed=False)

    assert [task.title for _, task in incomplete] == ["Evening meds"]


def test_filter_tasks_with_no_matching_pet_returns_empty_list():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", "walk"))
    owner.add_pet(pet)

    filtered = scheduler.filter_tasks(owner.get_all_tasks(), pet_name="Nonexistent")

    assert filtered == []


# --- Plan generation ---

def test_generate_plan_skips_tasks_that_dont_fit_available_time():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=10)

    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", "walk"))
    pet.add_task(Task("Breakfast", 10, "high", "feeding"))
    owner.add_pet(pet)

    plan = scheduler.generate_plan(owner)

    included = {item.task.title: item.included for item in plan}
    assert included == {"Morning walk": False, "Breakfast": True}


def test_generate_plan_excludes_already_completed_tasks():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    pet = Pet("Mochi", "dog")
    done = Task("Morning walk", 30, "high", "walk")
    done.mark_complete()
    pet.add_task(done)
    owner.add_pet(pet)

    plan = scheduler.generate_plan(owner)

    assert plan == []


def test_generate_plan_handles_owner_with_no_pets():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)

    assert scheduler.generate_plan(owner) == []


# --- Next available slot ---

def test_find_next_available_slot_returns_gap_between_tasks():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)

    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00", due_date=today))
    pet.add_task(Task("Breakfast", 10, "high", "feeding", scheduled_time="08:45", due_date=today))
    owner.add_pet(pet)

    slot = scheduler.find_next_available_slot(owner, due_date=today, duration_minutes=10)

    # Morning walk runs 08:00-08:30, leaving a 15-minute gap before Breakfast at 08:45.
    assert slot == "08:30"


def test_find_next_available_slot_returns_none_when_day_is_full():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)

    pet = Pet("Mochi", "dog")
    pet.add_task(Task("All day event", 780, "high", "walk", scheduled_time="08:00", due_date=today))
    owner.add_pet(pet)

    slot = scheduler.find_next_available_slot(
        owner, due_date=today, duration_minutes=30, day_start="08:00", day_end="21:00"
    )

    assert slot is None


def test_find_next_available_slot_ignores_completed_tasks():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)

    pet = Pet("Mochi", "dog")
    done = Task("Morning walk", 30, "high", "walk", scheduled_time="08:00", due_date=today)
    done.mark_complete()
    pet.add_task(done)
    owner.add_pet(pet)

    slot = scheduler.find_next_available_slot(owner, due_date=today, duration_minutes=10, day_start="08:00")

    assert slot == "08:00"


# --- Persistence (save_to_json / load_from_json) ---

def test_save_and_load_json_round_trip(tmp_path):
    today = date(2026, 1, 1)
    owner = Owner(name="Jordan", available_minutes=90, preferences="mornings only")

    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", 30, "high", "walk", frequency="daily", scheduled_time="08:00", due_date=today))
    done_task = Task("Breakfast", 10, "high", "feeding", scheduled_time="08:30", due_date=today)
    done_task.mark_complete()
    mochi.add_task(done_task)
    owner.add_pet(mochi)

    filepath = tmp_path / "data.json"
    owner.save_to_json(str(filepath))
    reloaded = Owner.load_from_json(str(filepath))

    assert reloaded.name == owner.name
    assert reloaded.available_minutes == owner.available_minutes
    assert reloaded.preferences == owner.preferences
    assert [p.name for p in reloaded.pets] == ["Mochi"]

    reloaded_tasks = {t.title: t for t in reloaded.pets[0].tasks}
    assert reloaded_tasks["Morning walk"].due_date == today
    assert reloaded_tasks["Morning walk"].frequency == "daily"
    assert reloaded_tasks["Morning walk"].completed is False
    assert reloaded_tasks["Breakfast"].completed is True


def test_load_from_json_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        Owner.load_from_json("this_file_does_not_exist.json")


def test_save_to_json_handles_owner_with_no_pets(tmp_path):
    owner = Owner(name="Jordan", available_minutes=60)
    filepath = tmp_path / "data.json"

    owner.save_to_json(str(filepath))
    reloaded = Owner.load_from_json(str(filepath))

    assert reloaded.pets == []


# --- Weekly task rescheduling ---

def test_reschedule_weekly_task_returns_none_for_non_recurring_task():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    task = Task("One-time vet visit", 30, "high", "meds", frequency="once")

    assert scheduler.reschedule_weekly_task(owner, task) is None


def test_reschedule_weekly_task_keeps_original_time_when_no_conflict():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)

    pet = Pet("Mochi", "dog")
    task = Task("Grooming", 30, "medium", "grooming", frequency="weekly", scheduled_time="10:00", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)

    rescheduled = scheduler.reschedule_weekly_task(owner, task)

    assert rescheduled.due_date == today + timedelta(weeks=1)
    assert rescheduled.scheduled_time == "10:00"


def test_reschedule_weekly_task_finds_a_different_slot_when_next_occurrence_conflicts():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)
    next_week = today + timedelta(weeks=1)

    pet = Pet("Mochi", "dog")
    task = Task("Grooming", 30, "medium", "grooming", frequency="weekly", scheduled_time="10:00", due_date=today)
    pet.add_task(task)
    # Blocks 10:00-10:30 on next_week, overlapping the naive next occurrence.
    pet.add_task(Task("Vet checkup", 20, "high", "meds", scheduled_time="10:15", due_date=next_week))
    owner.add_pet(pet)

    rescheduled = scheduler.reschedule_weekly_task(owner, task)

    assert rescheduled.due_date == next_week
    assert rescheduled.scheduled_time != "10:00"
    assert rescheduled.scheduled_time == "08:00"  # earliest open gap that day


def test_reschedule_weekly_task_advances_to_next_day_when_day_is_fully_booked():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)
    next_week = today + timedelta(weeks=1)

    pet = Pet("Mochi", "dog")
    task = Task("Grooming", 30, "medium", "grooming", frequency="weekly", scheduled_time="10:00", due_date=today)
    pet.add_task(task)
    # Fully books next_week from 08:00-21:00 (the default search window).
    pet.add_task(Task("All day event", 780, "high", "meds", scheduled_time="08:00", due_date=next_week))
    owner.add_pet(pet)

    rescheduled = scheduler.reschedule_weekly_task(owner, task)

    assert rescheduled.due_date == next_week + timedelta(days=1)
    assert rescheduled.scheduled_time == "10:00"  # no conflict the following day


def test_reschedule_weekly_task_returns_none_when_no_slot_found_in_window():
    scheduler = Scheduler()
    owner = Owner(name="Jordan", available_minutes=90)
    today = date(2026, 1, 1)
    next_week = today + timedelta(weeks=1)

    pet = Pet("Mochi", "dog")
    task = Task("Grooming", 30, "medium", "grooming", frequency="weekly", scheduled_time="10:00", due_date=today)
    pet.add_task(task)
    # Fully books every day in the default 7-day search window.
    for offset in range(8):
        pet.add_task(
            Task(
                f"Blocker {offset}",
                780,
                "high",
                "meds",
                scheduled_time="08:00",
                due_date=next_week + timedelta(days=offset),
            )
        )
    owner.add_pet(pet)

    assert scheduler.reschedule_weekly_task(owner, task) is None
