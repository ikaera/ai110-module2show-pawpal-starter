"""PawPal+ logic layer: pet care task tracking and daily plan scheduling."""

from dataclasses import dataclass, field
from typing import List

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str  # "walk", "feeding", "meds", "enrichment", "grooming"
    frequency: str = "daily"  # "daily", "weekly", etc.
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)
    preferences: str = ""

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Pet]:
        """Flatten tasks across all of this owner's pets, paired with their pet."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet, task))
        return all_tasks


@dataclass
class PlannedItem:
    task: Task
    pet_name: str
    included: bool
    reason: str


class Scheduler:
    """The "brain": retrieves tasks from an Owner's pets and builds a daily plan."""

    def generate_plan(self, owner: Owner) -> List[PlannedItem]:
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
