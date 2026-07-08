from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
        """Order tasks by priority (high first), then by clock time."""
        # Unknown priorities sort last (99); tasks with no time sort last ("99:99").
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.time or "99:99"),
        )

    def filter_by_time_budget(self, tasks: List[Task], budget: int) -> List[Task]:
        """Greedily keep tasks (in priority order) until the minute budget runs out."""
        kept, spent = [], 0
        for task in self.sort_by_priority(tasks):
            if spent + task.duration <= budget:
                kept.append(task)
                spent += task.duration
        return kept

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return a warning for each clock time used by more than one task."""
        seen, warnings = {}, []
        for task in tasks:
            if task.time:
                seen.setdefault(task.time, []).append(task.description)
        for time, descs in seen.items():
            if len(descs) > 1:
                warnings.append(f"Conflict at {time}: {', '.join(descs)}")
        return warnings

    def advance_recurring(self, task: Task) -> Optional[Task]:
        """When a daily/weekly task is completed, return its next occurrence."""
        if task.frequency == "once":
            return None
        step = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_time = task.time
        if task.time and _is_datestamp(task.time):
            next_time = (datetime.strptime(task.time, "%Y-%m-%d") + step).strftime("%Y-%m-%d")
        return Task(
            description=task.description,
            duration=task.duration,
            priority=task.priority,
            category=task.category,
            time=next_time,
            completed=False,
            frequency=task.frequency,
        )

    def generate_plan(self, owner: Owner):
        """Produce the sorted, budget-limited plan plus a reasoning string."""
        all_tasks = owner.get_all_tasks()
        planned = self.filter_by_time_budget(all_tasks, owner.time_available)
        conflicts = self.detect_conflicts(planned)

        used = sum(t.duration for t in planned)
        deferred = len(all_tasks) - len(planned)
        reasoning = (
            f"Chose {len(planned)} of {len(all_tasks)} task(s), "
            f"{used}/{owner.time_available} min used, "
            f"sorted by priority then time"
        )
        if deferred:
            reasoning += f"; {deferred} deferred (over budget)"
        if conflicts:
            reasoning += f"; {len(conflicts)} time conflict(s)"
        return planned, reasoning
    
def _is_datestamp(value: str) -> bool:
    """True if a string looks like YYYY-MM-DD."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False