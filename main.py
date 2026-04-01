#!/usr/bin/env python3
"""
PawPal+ Demo Script

Temporary testing ground to verify backend logic works in the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

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

    pet1.add_task(task1)
    pet1.add_task(task2)
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
    
    if scheduler.overflow_tasks:
        print("\nOverflow tasks:")
        for task in scheduler.overflow_tasks:
            duration_min = task.duration_min
            duration_str = f"{duration_min // 60} hour{'s' if duration_min // 60 > 1 else ''}" if duration_min % 60 == 0 and duration_min > 0 else f"{duration_min} min"
            print(f"  - {task.description} ({task.priority}, {duration_str})")

if __name__ == "__main__":
    main()