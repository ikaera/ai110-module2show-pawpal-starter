import os
from datetime import date, time

import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** helps a busy pet owner plan care tasks across one or more pets: add tasks with a
priority and scheduled time, then generate a time-budgeted daily plan, view tasks sorted
chronologically, filter by pet or completion status, and get warned about scheduling conflicts.
"""
)

scheduler = Scheduler()

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available time today (minutes)", min_value=1, max_value=600, value=60)

# Create the Owner once per session; reused on every rerun instead of being
# rebuilt from scratch each time Streamlit reruns the script. If a data.json
# from a previous run exists, load it so pets/tasks persist across restarts.
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
        st.toast(f"Loaded saved data from {DATA_FILE}.")
    else:
        st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)

owner = st.session_state.owner

st.markdown("### Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species))
    owner.save_to_json(DATA_FILE)

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks with a scheduled time — this feeds sorting, conflict detection, and the daily plan below.")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Which pet is this task for?", pet_names)
    pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        scheduled_time = st.time_input("Scheduled time", value=time(9, 0))
    with col5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

    if st.button("Add task"):
        pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category="general",
                frequency=frequency,
                scheduled_time=scheduled_time.strftime("%H:%M"),
            )
        )
        owner.save_to_json(DATA_FILE)

    if pet.tasks:
        st.write(f"Current tasks for {pet.name}:")
        for task in pet.tasks:
            t_col1, t_col2 = st.columns([4, 1])
            with t_col1:
                status = "✅" if task.completed else "⬜"
                st.write(
                    f"{status} **{task.scheduled_time}** — {task.title} "
                    f"({task.duration_minutes} min, {task.priority} priority, {task.frequency})"
                )
            with t_col2:
                if not task.completed and st.button("Mark done", key=f"complete-{pet.name}-{id(task)}"):
                    next_task = pet.complete_task(task)
                    owner.save_to_json(DATA_FILE)
                    if next_task is not None:
                        st.toast(f"Recurring task — next occurrence created for {next_task.due_date}.")
                    st.rerun()
    else:
        st.info(f"No tasks yet for {pet.name}. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

st.subheader("All Tasks — Sorted by Time")

all_tasks = [task for _, task in owner.get_all_tasks()]
if all_tasks:
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    st.table(
        [
            {
                "time": t.scheduled_time,
                "title": t.title,
                "priority": t.priority,
                "completed": t.completed,
            }
            for t in sorted_tasks
        ]
    )
else:
    st.info("No tasks yet.")

st.subheader("Filter Tasks")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
with filter_col2:
    status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])

filtered = owner.get_all_tasks()
filtered = scheduler.filter_tasks(
    filtered,
    pet_name=None if pet_filter == "All" else pet_filter,
    completed=None if status_filter == "All" else status_filter == "Completed",
)
if filtered:
    st.table(
        [
            {"pet": pet.name, "time": task.scheduled_time, "title": task.title, "completed": task.completed}
            for pet, task in filtered
        ]
    )
else:
    st.info("No tasks match this filter.")

st.divider()

st.subheader("Scheduling Conflicts")
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No conflicts detected.")

st.divider()

st.subheader("Find Next Available Slot")
st.caption("Find the earliest open slot today that's long enough for a new task.")

slot_duration = st.number_input("New task duration (minutes)", min_value=1, max_value=240, value=20, key="slot_duration")
if st.button("Find next available slot"):
    slot = scheduler.find_next_available_slot(owner, due_date=date.today(), duration_minutes=int(slot_duration))
    if slot:
        st.success(f"Next available slot: {slot}")
    else:
        st.warning("No slot available today.")

st.divider()

st.subheader("Today's Plan")
st.caption("Highest priority tasks are scheduled first within your available time.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan(owner)
    if not plan:
        st.info("No pending tasks to schedule.")
    for item in plan:
        message = f"{item.pet_name}: {item.task.title} ({item.task.duration_minutes} min) — {item.reason}"
        if item.included:
            st.success(message)
        else:
            st.warning(message)
