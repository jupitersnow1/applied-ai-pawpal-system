#!/usr/bin/env python3
"""
PawPal+ Demo Script

Temporary testing ground to verify backend logic works in the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, ScheduleEntry
from datetime import date, timedelta, datetime

def main():
    # Create an Owner
    owner = Owner(id="owner1", name="Alice", available_time_min=120)  # 2 hours available

    # Create two Pets
    pet1 = Pet(id="pet1", name="Buddy", species="Dog", age=3)
    pet2 = Pet(id="pet2", name="Whiskers", species="Cat", age=2)

    # Add pets to owner
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Create and add tasks to pets
    task1 = Task(id="task1", description="Morning walk", duration_min=30, priority="high", frequency="daily")
    task2 = Task(id="task2", description="Feed breakfast", duration_min=15, priority="medium", frequency="daily")
    task3 = Task(id="task3", description="Playtime", duration_min=45, priority="low", frequency="daily")
    task4 = Task(id="task4", description="Vet checkup", duration_min=60, priority="high", frequency="once")
    task5 = Task(id="task5", description="Bath time", duration_min=20, priority="medium", frequency="weekly",
                 last_scheduled=date.today() - timedelta(days=3))  # scheduled 3 days ago — not due yet

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet1.add_task(task4)  # once — should be scheduled
    pet1.add_task(task5)  # weekly, done 3 days ago — should be skipped
    pet2.add_task(task3)

    # Create Scheduler and build daily plan
    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()

    # Print Today's Schedule
    print(f"Today's Schedule for Owner: {owner.name}")
    for pet in owner.pets:
        print(f"  Pet: {pet.name} ({pet.species})")
        pet_tasks = [entry for entry in scheduler.schedule if entry.pet == pet]
        if pet_tasks:
            for entry in pet_tasks:
                duration_min = entry.task.duration_min
                duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
                print(f"    - {entry.task.description} ({entry.task.priority}, {duration_str}, {entry.start.strftime('%H:%M')} - {entry.end.strftime('%H:%M')})")
        else:
            print("    - No tasks scheduled")
    
    print("\nTimeline (sorted by start time):")
    for entry in scheduler.sort_by_time():
        print(f"  {entry.start.strftime('%H:%M')} - {entry.end.strftime('%H:%M')}  [{entry.pet.name}] {entry.task.description}")

    print("\nConflict detection (normal schedule — expect none):")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for a, b in conflicts:
            print(f"  CONFLICT: '{a.task.description}' ({a.start.strftime('%H:%M')}-{a.end.strftime('%H:%M')}) "
                  f"overlaps '{b.task.description}' ({b.start.strftime('%H:%M')}-{b.end.strftime('%H:%M')})")
    else:
        print("  No conflicts found.")

    # Manually inject an overlapping entry to prove detection works
    fake_start = scheduler.schedule[0].start
    fake_end = fake_start + timedelta(minutes=10)
    overlap_task = Task(id="overlap1", description="Overlapping task", duration_min=10, priority="low")
    overlap_pet = owner.pets[0]
    scheduler.schedule.append(ScheduleEntry(task=overlap_task, pet=overlap_pet, start=fake_start, end=fake_end))

    print("\nConflict detection (after injecting overlap — expect 1):")
    for a, b in scheduler.detect_conflicts():
        print(f"  CONFLICT: '{a.task.description}' ({a.start.strftime('%H:%M')}-{a.end.strftime('%H:%M')}) "
              f"overlaps '{b.task.description}' ({b.start.strftime('%H:%M')}-{b.end.strftime('%H:%M')})")

    print("\nRecurrence check:")
    print(f"  Bath time is_due today: {task5.is_due(date.today())} (weekly, last done 3 days ago — expect False)")
    print(f"  Vet checkup is_due today: {task4.is_due(date.today())} (once, not complete — expect True)")

    print("\nFilter: Buddy's pending tasks:")
    for t in owner.filter_tasks(pet_id="pet1", status="pending"):
        print(f"  - {t.description} ({t.priority})")

    task1.mark_complete()
    print("\nFilter: all complete tasks after marking task1 done:")
    for t in owner.filter_tasks(status="complete"):
        print(f"  - {t.description}")

    if scheduler.overflow_tasks:
        print("\nOverflow tasks:")
        for task in scheduler.overflow_tasks:
            duration_min = task.duration_min
            duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
            print(f"  - {task.description} ({task.priority}, {duration_str})")

if __name__ == "__main__":
    main()