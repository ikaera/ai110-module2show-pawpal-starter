"""PawPal+ logic layer: pet care task tracking and daily plan scheduling."""

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _time_to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = map(int, hhmm.split(":"))
    return hours * 60 + minutes


def _minutes_to_time(total_minutes: int) -> str:
    """Convert minutes since midnight back to an "HH:MM" string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str  # "walk", "feeding", "meds", "enrichment", "grooming"
    frequency: str = "daily"  # "daily", "weekly", etc.
    completed: bool = False
    scheduled_time: str = "09:00"  # "HH:MM", 24-hour format
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, incomplete copy of this task due at its next recurrence, or None if it doesn't recur."""
        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            completed=False,
            scheduled_time=self.scheduled_time,
            due_date=self.due_date + interval,
        )

    def to_dict(self) -> dict:
        """Convert this task to a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "frequency": self.frequency,
            "completed": self.completed,
            "scheduled_time": self.scheduled_time,
            "due_date": self.due_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dictionary produced by to_dict()."""
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            category=data["category"],
            frequency=data.get("frequency", "daily"),
            completed=data.get("completed", False),
            scheduled_time=data.get("scheduled_time", "09:00"),
            due_date=date.fromisoformat(data["due_date"]),
        )


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def to_dict(self) -> dict:
        """Convert this pet (and its tasks) to a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its tasks) from a dictionary produced by to_dict()."""
        pet = cls(name=data["name"], species=data["species"])
        pet.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return pet

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add and return its next occurrence."""
        task.mark_complete()
        next_task = task.get_next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)
    preferences: str = ""

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Flatten tasks across all of this owner's pets, paired with their pet."""
        all_tasks: List[Tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet, task))
        return all_tasks

    def to_dict(self) -> dict:
        """Convert this owner (and all pets/tasks) to a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (and all pets/tasks) from a dictionary produced by to_dict()."""
        owner = cls(
            name=data["name"],
            available_minutes=data["available_minutes"],
            preferences=data.get("preferences", ""),
        )
        owner.pets = [Pet.from_dict(pet_data) for pet_data in data.get("pets", [])]
        return owner

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Save this owner's full state (pets and tasks) to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load an owner's full state (pets and tasks) from a JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class PlannedItem:
    task: Task
    pet_name: str
    included: bool
    reason: str


class Scheduler:
    """The "brain": retrieves tasks from an Owner's pets and builds a daily plan."""

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted earliest-to-latest by their scheduled_time ("HH:MM")."""
        # "HH:MM" strings sort correctly with plain string comparison since
        # both halves are always zero-padded to 2 digits (e.g. "09:00" < "10:00").
        return sorted(tasks, key=lambda t: t.scheduled_time)

    def sort_by_priority_then_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by priority (high, then medium, then low), ties broken by scheduled_time."""
        return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.scheduled_time))

    def detect_conflicts(self, owner: Owner) -> List[str]:
        """Return a warning message for each due_date + scheduled_time shared by more than one task."""
        tasks_by_slot: dict = {}
        for pet, task in owner.get_all_tasks():
            slot = (task.due_date, task.scheduled_time)
            tasks_by_slot.setdefault(slot, []).append((pet, task))

        warnings = []
        for (due_date, scheduled_time), group in tasks_by_slot.items():
            if len(group) > 1:
                clashing = ", ".join(f"{pet.name}'s '{task.title}'" for pet, task in group)
                warnings.append(f"Conflict on {due_date} at {scheduled_time}: {clashing}")
        return warnings

    def filter_tasks(
        self,
        pet_tasks: List[Tuple[Pet, Task]],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Tuple[Pet, Task]]:
        """Filter (pet, task) pairs by pet name and/or completion status."""
        result = pet_tasks
        if pet_name is not None:
            result = [(pet, task) for pet, task in result if pet.name == pet_name]
        if completed is not None:
            result = [(pet, task) for pet, task in result if task.completed == completed]
        return result

    def find_next_available_slot(
        self,
        owner: Owner,
        due_date: date,
        duration_minutes: int,
        day_start: str = "08:00",
        day_end: str = "21:00",
    ) -> Optional[str]:
        """Return the earliest "HH:MM" slot on due_date with at least duration_minutes free, or None."""
        day_tasks = [
            task
            for _, task in owner.get_all_tasks()
            if task.due_date == due_date and not task.completed
        ]
        day_tasks.sort(key=lambda t: t.scheduled_time)

        busy_blocks = [
            (_time_to_minutes(task.scheduled_time), _time_to_minutes(task.scheduled_time) + task.duration_minutes)
            for task in day_tasks
        ]

        cursor = _time_to_minutes(day_start)
        end_of_day = _time_to_minutes(day_end)

        for start, end in busy_blocks:
            if start - cursor >= duration_minutes:
                return _minutes_to_time(cursor)
            cursor = max(cursor, end)

        if end_of_day - cursor >= duration_minutes:
            return _minutes_to_time(cursor)

        return None

    def reschedule_weekly_task(
        self,
        owner: Owner,
        task: Task,
        max_extra_days: int = 7,
    ) -> Optional[Task]:
        """Return the task's next occurrence, nudged forward to avoid a scheduling conflict.

        Starts from the task's normal next occurrence (due_date advanced by its recurrence
        interval). If that exact time slot is free, it's kept as-is. If another task's duration
        overlaps it, this searches forward day-by-day (up to max_extra_days) using
        find_next_available_slot for the earliest open gap long enough for the task. Returns
        None if the task doesn't recur, or if no open slot is found within the search window.

        Note: when a conflict pushes the task to a new day, the new time is the *earliest*
        open gap that day (per find_next_available_slot), not necessarily the time closest to
        the task's original scheduled_time.
        """
        next_task = task.get_next_occurrence()
        if next_task is None:
            return None

        for extra_days in range(max_extra_days + 1):
            candidate_date = next_task.due_date + timedelta(days=extra_days)
            start = _time_to_minutes(next_task.scheduled_time)
            end = start + next_task.duration_minutes

            conflict = any(
                other.due_date == candidate_date
                and _time_to_minutes(other.scheduled_time) < end
                and _time_to_minutes(other.scheduled_time) + other.duration_minutes > start
                for _, other in owner.get_all_tasks()
            )

            if not conflict:
                next_task.due_date = candidate_date
                return next_task

            slot = self.find_next_available_slot(owner, candidate_date, next_task.duration_minutes)
            if slot is not None:
                next_task.due_date = candidate_date
                next_task.scheduled_time = slot
                return next_task

        return None

    def generate_plan(self, owner: Owner) -> List[PlannedItem]:
        """Build today's plan by prioritizing the owner's pending tasks within their available time."""
        pet_tasks = owner.get_all_tasks()

        # Only incomplete tasks need scheduling today.
        pending = [(pet, task) for pet, task in pet_tasks if not task.completed]

        # Highest priority first; shorter tasks break ties so more can fit.
        pending.sort(key=lambda pt: (PRIORITY_ORDER.get(pt[1].priority, 99), pt[1].duration_minutes))

        plan: List[PlannedItem] = []
        remaining_minutes = owner.available_minutes

        for pet, task in pending:
            if task.duration_minutes <= remaining_minutes:
                remaining_minutes -= task.duration_minutes
                plan.append(
                    PlannedItem(
                        task=task,
                        pet_name=pet.name,
                        included=True,
                        reason=(
                            f"Included: {task.priority} priority, "
                            f"fits in remaining {remaining_minutes + task.duration_minutes} min"
                        ),
                    )
                )
            else:
                plan.append(
                    PlannedItem(
                        task=task,
                        pet_name=pet.name,
                        included=False,
                        reason=(
                            f"Skipped: needs {task.duration_minutes} min, "
                            f"only {remaining_minutes} min remaining"
                        ),
                    )
                )

        return plan
