"""CLI demo for PawPal+. Verifies the backend logic before the Streamlit UI."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # 1. Create an owner with a daily time budget.
    owner = Owner(name="Markian", time_available=120)

    # 2. Create two pets.
    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    milo = Pet(name="Milo", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(milo)

    # 3. Add tasks with different times, durations, and priorities.
    biscuit.add_task(Task("Morning walk", duration=30, priority="high",
                          category="walk", time="08:00"))
    biscuit.add_task(Task("Feeding", duration=10, priority="high",
                          category="feeding", time="09:00"))
    milo.add_task(Task("Litter change", duration=5, priority="med",
                       category="grooming", time="10:00"))
    milo.add_task(Task("Playtime", duration=15, priority="low",
                       category="enrichment", time="17:00"))

    # 4. Print a "Today's Schedule" by walking each pet.
    scheduler = Scheduler()
    tasks, reasoning = scheduler.generate_plan(owner)

    print(f"\nToday's Schedule for {owner.name} "
          f"(budget: {owner.time_available} min)")
    print("=" * 48)
    for pet in owner.pets:
        print(f"\n{pet.name} ({pet.species}):")
        for t in pet.tasks:
            status = "done" if t.completed else "todo"
            print(f"  {t.time or '--:--'}  {t.description:<15} "
                  f"({t.duration} min) [priority: {t.priority}] [{status}]")

    print("\n" + "-" * 48)
    print(f"Plan reasoning: {reasoning}")


if __name__ == "__main__":
    main()