"""PawPal+ logic layer: pet care task tracking and daily plan scheduling."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str  # "walk", "feeding", "meds", "enrichment", "grooming"


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: str = ""


class Planner:
    def generate_plan(self, pet: Pet, owner: Owner) -> list:
        pass
