import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", time_available=120)
    st.session_state.owner.add_pet(Pet(name="Mochi", species="dog"))

owner = st.session_state.owner
pet = owner.pets[0]          # this starter UI manages a single pet
scheduler = Scheduler()

with st.expander("Scenario", expanded=False):
    st.markdown(
        "**PawPal+** helps a pet owner plan care tasks based on constraints "
        "like time, priority, and preferences."
    )

st.divider()

# --- Owner + pet info -----------------------------------------------------
st.subheader("Owner & Pet")
owner.name = st.text_input("Owner name", value=owner.name)
pet.name = st.text_input("Pet name", value=pet.name)
pet.species = st.selectbox(
    "Species", ["dog", "cat", "other"],
    index=["dog", "cat", "other"].index(pet.species) if pet.species in ["dog", "cat", "other"] else 0,
)
owner.time_available = st.number_input(
    "Daily time budget (minutes)", min_value=0, value=owner.time_available, step=15
)

st.divider()

# --- Add tasks ------------------------------------------------------------
st.markdown("### Tasks")
st.caption("Each task you add becomes a real Task object attached to your pet.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "med", "low"], index=0)

task_time = st.text_input("Time (HH:MM, optional)", value="")

if st.button("Add task"):
    if task_title.strip():
        pet.add_task(Task(
            description=task_title.strip(),
            duration=int(duration),
            priority=priority,
            time=task_time.strip() or None,
        ))
        st.success(f"Added '{task_title}' to {pet.name}")
    else:
        st.warning("Give the task a title first.")

# Display current tasks straight from the Pet object (not a separate dict list).
if pet.tasks:
    st.write("Current tasks:")
    st.table([
        {
            "title": t.description,
            "duration_minutes": t.duration,
            "priority": t.priority,
            "time": t.time or "--:--",
            "done": t.completed,
        }
        for t in pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Build schedule -------------------------------------------------------
st.subheader("Build Schedule")

# Phase 6: surface the Scheduler's smart features in the UI.
if st.button("Generate schedule"):
    planned, reasoning = scheduler.generate_plan(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    if planned:
        # Show any time conflicts as warnings the owner can act on.
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

        st.markdown(f"**Daily plan for {pet.name} ({pet.species})**")

        # planned is already sorted by priority then time.
        st.table([
            {
                "time": t.time or "--:--",
                "task": t.description,
                "duration": f"{t.duration} min",
                "priority": t.priority,
            }
            for t in planned
        ])

        st.success(reasoning)
    else:
        st.info("Add at least one task first.")
