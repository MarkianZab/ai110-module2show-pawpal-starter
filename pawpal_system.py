from dataclasses import dataclass, field
from typing import List, Optional


# Priority is ranked, not alphabetical: high beats med beats low.
# We'll use this in Phase 2 to sort by priority over clock time.
PRIORITY_ORDER = {"high": 0, "med": 1, "low": 2}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""
    description: str
    duration: int                     # minutes
    priority: str = "med"             # "high", "med", "low"
    category: str = "general"         # walk, feeding, meds, grooming, etc.
    time: Optional[str] = None        # optional "HH:MM"
    completed: bool = False
    frequency: str = "once"           # "once" or "daily" or "weekly"

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet owned by the user, with its own list of care tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a task to this pet."""
        self.tasks.append(task)


class Owner:
    """The app user. Owns pets and has a daily time budget (minutes)."""

    def __init__(self, name: str, time_available: int = 120):
        self.name = name
        self.time_available = time_available
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    """The 'brain': turns an owner's tasks + constraints into a daily plan."""

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority first, then clock time."""
        ...

    def filter_by_time_budget(self, tasks: List[Task], budget: int) -> List[Task]:
        """Keep tasks that fit within the available minutes; defer the rest."""
        ...

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return warnings for tasks scheduled at the same clock time."""
        ...

    def generate_plan(self, owner: Owner):
        """Produce the daily plan (list of tasks) plus a short reasoning string."""
        tasks = owner.get_all_tasks()
        reasoning = (
            f"{len(tasks)} task(s) across {len(owner.pets)} pet(s). "
            f"Priority sorting and time-budget filtering arrive in Phase 4."
        )
        return tasks, reasoning