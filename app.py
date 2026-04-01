import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+! Plan your pet care tasks with ease.
"""
)

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = None
if "schedule_output" not in st.session_state:
    st.session_state.schedule_output = ""

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name")
col1, col2 = st.columns(2)
with col1:
    available_hours = st.number_input("Available hours", min_value=0, max_value=24, value=2, step=1, key="available_hours")
with col2:
    available_minutes = st.number_input("Available minutes", min_value=0, max_value=55, value=0, step=5, key="available_minutes")

available_time = available_hours * 60 + available_minutes
if available_time == 0:
    st.warning("Available time is zero; please select at least 5 minutes")

st.subheader("Pet Setup")
if "pets" not in st.session_state:
    st.session_state.pets = []

pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species")
age = st.number_input("Age", min_value=1, max_value=30, value=3, key="age")

if st.button("Add pet", key="add_pet"):
    pet_id = f"pet{len(st.session_state.pets)+1}"
    st.session_state.pets.append({"id": pet_id, "name": pet_name, "species": species, "age": age})

if st.session_state.pets:
    st.write("Current pets:")
    st.table(st.session_state.pets)
    selected_pet = st.selectbox("Assign task to pet", [p["id"] + ": " + p["name"] for p in st.session_state.pets], key="selected_pet")
    selected_pet_id = selected_pet.split(":")[0]
else:
    st.info("Add at least one pet first.")
    selected_pet_id = None

st.subheader("Tasks")
if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=20, step=5, key="duration")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority")

if st.button("Add task", key="add_task"):
    if selected_pet_id:
        st.session_state.tasks.append(
            {
                "pet_id": selected_pet_id,
                "title": task_title,
                "duration_minutes": int(duration),
                "priority": priority,
            }
        )
    else:
        st.error("Please add and select a pet first before adding tasks.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule", key="generate_schedule"):
    owner = Owner(id="owner1", name=owner_name, available_time_min=available_time)

    # Recreate pets from session state
    pet_lookup = {}
    for p_data in st.session_state.pets:
        pet_obj = Pet(id=p_data["id"], name=p_data["name"], species=p_data["species"], age=p_data["age"])
        owner.add_pet(pet_obj)
        pet_lookup[p_data["id"]] = pet_obj

    # Add tasks to proper pets
    for idx, t in enumerate(st.session_state.tasks, start=1):
        target_pet = pet_lookup.get(t.get("pet_id"))
        if not target_pet:
            continue
        task = Task(
            id=f"task{idx}",
            description=t["title"],
            duration_min=t["duration_minutes"],
            priority=t["priority"],
            frequency="daily"
        )
        target_pet.add_task(task)

    # Create Scheduler and build plan
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()
    
    # Format output
    output = f"Today's Schedule for Owner: {owner.name}\n\n"
    for p in owner.pets:
        output += f"Pet: {p.name} ({p.species})\n"
        pet_tasks = [entry for entry in scheduler.schedule if entry.pet == p]
        if pet_tasks:
            for entry in pet_tasks:
                duration_min = entry.task.duration_min
                duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
                output += (
                    f"  - {entry.task.description} ({entry.task.priority}, {duration_str}, "
                    f"{entry.start.strftime('%H:%M')} - {entry.end.strftime('%H:%M')})\n"
                )
        else:
            output += "  - No tasks scheduled\n"
    
    if scheduler.overflow_tasks:
        output += "\nOverflow tasks:\n"
        for task in scheduler.overflow_tasks:
            duration_min = task.duration_min
            duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
            output += f"  - {task.description} ({task.priority}, {duration_str})\n"
    
    st.session_state.schedule_output = output
    st.success("Schedule generated!")

if st.session_state.schedule_output:
    st.subheader("Generated Schedule")
    st.code(st.session_state.schedule_output, language="text")

