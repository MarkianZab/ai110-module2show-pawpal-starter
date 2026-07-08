"""CLI demo for PawPal+. Verifies the backend logic before the Streamlit UI."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Markian", time_available=60)   # tight budget on purpose

    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    milo = Pet(name="Milo", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(milo)

    # Added OUT OF ORDER and with mixed priorities to prove sorting works.
    biscuit.add_task(Task("Evening play", 15, priority="low", time="18:00"))
    biscuit.add_task(Task("Morning walk", 30, priority="high", time="08:00"))
    biscuit.add_task(Task("Vet meds", 10, priority="high", time="08:00"))  # conflict @ 08:00
    milo.add_task(Task("Feeding", 10, priority="med", time="09:00"))

    scheduler = Scheduler()

    print("\n--- All tasks, sorted by priority then time ---")
    for t in scheduler.sort_by_priority(owner.get_all_tasks()):
        print(f"  {t.time}  {t.description:<14} [{t.priority}] ({t.duration} min)")

    print("\n--- Conflicts ---")
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
    print("\n".join(f"  ⚠️  {c}" for c in conflicts) or "  none")

    print("\n--- Today's plan (within 60 min budget) ---")
    planned, reasoning = scheduler.generate_plan(owner)
    for t in planned:
        print(f"  {t.time}  {t.description:<14} [{t.priority}] ({t.duration} min)")
    print(f"\n  Reasoning: {reasoning}")

    print("\n--- Recurrence demo ---")
    daily = Task("Daily walk", 30, priority="high", time="2026-07-08", frequency="daily")
    daily.mark_complete()
    nxt = scheduler.advance_recurring(daily)
    print(f"  Completed {daily.time}; next occurrence generated for {nxt.time}")


if __name__ == "__main__":
    main()