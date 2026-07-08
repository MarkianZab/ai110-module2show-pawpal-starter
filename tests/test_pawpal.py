"""Test suite for PawPal+ core behavior and scheduling algorithms."""

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Phase 2: core behavior ----------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = Task(description="Feeding", duration=10)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task to a pet increases that pet's task count by one."""
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.tasks) == 0
    pet.add_task(Task(description="Morning walk", duration=30))
    assert len(pet.tasks) == 1


# --- Phase 5: scheduling algorithms --------------------------------------

def test_sort_by_priority_then_time():
    """Tasks come back high->med->low, with time breaking ties."""
    scheduler = Scheduler()
    tasks = [
        Task("Play", 15, priority="low", time="18:00"),
        Task("Meds", 10, priority="high", time="09:00"),
        Task("Walk", 30, priority="high", time="08:00"),
        Task("Feed", 10, priority="med", time="12:00"),
    ]
    result = scheduler.sort_by_priority(tasks)
    assert [t.description for t in result] == ["Walk", "Meds", "Feed", "Play"]


def test_filter_defers_tasks_over_budget():
    """Low-priority tasks are dropped once the minute budget is exhausted."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, priority="high"),
        Task("Meds", 20, priority="high"),
        Task("Play", 30, priority="low"),   # 80 total > 50 budget -> dropped
    ]
    kept = scheduler.filter_by_time_budget(tasks, budget=50)
    assert [t.description for t in kept] == ["Walk", "Meds"]


def test_detect_conflicts_flags_same_time():
    """Two tasks at the same clock time produce exactly one conflict warning."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, time="08:00"),
        Task("Meds", 10, time="08:00"),
        Task("Feed", 10, time="09:00"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_recurrence_generates_next_day():
    """Completing a daily task yields a fresh, incomplete task for the next day."""
    scheduler = Scheduler()
    daily = Task("Walk", 30, priority="high", time="2026-07-08", frequency="daily")
    daily.mark_complete()
    nxt = scheduler.advance_recurring(daily)
    assert nxt is not None
    assert nxt.completed is False
    assert nxt.time == "2026-07-09"


def test_once_task_does_not_recur():
    """A one-off task has no next occurrence."""
    scheduler = Scheduler()
    once = Task("Vet visit", 60, frequency="once", time="2026-07-08")
    assert scheduler.advance_recurring(once) is None


# --- Phase 5: edge cases -------------------------------------------------

def test_pet_with_no_tasks_produces_empty_plan():
    """An owner whose pet has no tasks gets an empty plan, not an error."""
    scheduler = Scheduler()
    owner = Owner("Markian", time_available=60)
    owner.add_pet(Pet("Biscuit", "dog"))
    planned, reasoning = scheduler.generate_plan(owner)
    assert planned == []
    assert "0 of 0" in reasoning


def test_zero_budget_keeps_nothing():
    """A zero-minute budget defers every task."""
    scheduler = Scheduler()
    tasks = [Task("Walk", 30, priority="high")]
    assert scheduler.filter_by_time_budget(tasks, budget=0) == []