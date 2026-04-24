#!/usr/bin/env python3
"""
PawPal+ Applied AI System — End-to-End Demo

Mirrors the Streamlit app workflow in the terminal:
  Step 1 — Owner Setup
  Step 2 — Pet Setup
  Step 3 — Add Tasks Manually
  Step 4 — Add Tasks with AI (natural language parser + guardrails)
  Step 5 — Build Schedule (priority-based algorithm)
  Step 6 — Recurrence & Filters
  Step 7 — AI Schedule Critique (agentic tool-use analysis)
"""

from dotenv import load_dotenv
load_dotenv()

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_parser import parse_task_from_text
from schedule_critic import critique_schedule

DIVIDER = "─" * 62


def header() -> None:
    print(f"\n{'🐾 PawPal+ Applied AI System':^62}")
    print(f"{'End-to-End Demo':^62}")
    print(DIVIDER)


def section(step: str, title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {step}: {title}")
    print(f"{DIVIDER}\n")


def parse_and_assign(prompt: str, label: str, pets: list) -> None:
    """Parse a natural language prompt and assign tasks to matching pets."""
    known = {p.name.lower(): p for p in pets}
    print(f"  [{label}]")
    print(f"  Input: \"{prompt}\"")
    try:
        parsed_tasks = parse_task_from_text(prompt, pets=pets)
        for parsed in parsed_tasks:
            mentioned = parsed.get("mentioned_name")
            if mentioned:
                matched = known.get(mentioned.lower())
                if matched:
                    task_id = f"ai_{sum(len(p.tasks) for p in pets) + 1}"
                    matched.add_task(Task(
                        id=task_id,
                        description=parsed["description"],
                        duration_min=parsed["duration_min"],
                        priority=parsed["priority"],
                        frequency=parsed["frequency"],
                    ))
                    print(f"  ✅ {matched.name} ← '{parsed['description']}' "
                          f"| {parsed['duration_min']} min | {parsed['priority']} | {parsed['frequency']}")
                else:
                    print(f"  ⚠️  '{mentioned}' not in pet list — "
                          f"skipped '{parsed['description']}'. Add {mentioned} in Pet Setup first.")
            else:
                print(f"  ℹ️  No pet mentioned — '{parsed['description']}' needs manual assignment.")
    except Exception as e:
        print(f"  ❌ Parser error: {e}")
    print()


def main():

    header()

    # ── Step 1: Owner Setup ───────────────────────────────────────────────────
    section("Step 1", "Owner Setup")

    owner = Owner(id="owner1", name="Alice", available_time_min=120)
    print(f"  Name           : {owner.name}")
    print(f"  Available time : {owner.available_time_min} min")

    # ── Step 2: Pet Setup ─────────────────────────────────────────────────────
    section("Step 2", "Pet Setup")

    buddy    = Pet(id="pet1", name="Buddy",    species="dog", age=3)
    whiskers = Pet(id="pet2", name="Whiskers", species="cat", age=2)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    print(f"  {'ID':<6}  {'NAME':<10}  {'SPECIES':<6}  AGE")
    print(f"  {'─'*6}  {'─'*10}  {'─'*6}  {'─'*3}")
    for p in owner.pets:
        print(f"  {p.id:<6}  {p.name:<10}  {p.species:<6}  {p.age}")

    # ── Step 3: Add Tasks Manually ────────────────────────────────────────────
    section("Step 3", "Add Tasks Manually")

    buddy.add_task(Task(id="m1", description="Playtime",    duration_min=45, priority="low",    frequency="daily"))
    buddy.add_task(Task(id="m2", description="Bath time",   duration_min=20, priority="medium", frequency="weekly",
                        last_scheduled=date.today() - timedelta(days=3)))
    whiskers.add_task(Task(id="m3", description="Litter box", duration_min=10, priority="high", frequency="daily"))

    print(f"  {'PET':<10}  {'TASK':<14}  {'DURATION':>8}  {'PRIORITY':<8}  FREQUENCY")
    print(f"  {'─'*10}  {'─'*14}  {'─'*8}  {'─'*8}  {'─'*9}")
    for p in owner.pets:
        for t in p.tasks:
            print(f"  {p.name:<10}  {t.description:<14}  {t.duration_min:>6} min"
                  f"  {t.priority:<8}  {t.frequency}")

    # ── Step 4: Add Tasks with AI ─────────────────────────────────────────────
    section("Step 4", "Add Tasks with AI (Natural Language Parser)")

    # Example 1 — single task, one pet
    parse_and_assign(
        "Walk Buddy for 30 minutes every morning — high priority.",
        "Single task, one pet",
        owner.pets,
    )

    # Example 2 — multiple tasks across multiple pets in one prompt
    parse_and_assign(
        "Feed Buddy and Whiskers early morning, around 15 min each. Groom Whiskers for 30 min after.",
        "Multiple tasks, multiple pets",
        owner.pets,
    )

    # Example 3 — unregistered pet triggers guardrail warning
    parse_and_assign(
        "Give Luna her weekly bath, should take about 20 minutes.",
        "Unknown pet — guardrail demo",
        owner.pets,
    )

    # Example 4 — explicit once frequency and high priority
    parse_and_assign(
        "Take Buddy to the vet this Saturday, one time only, high priority — about an hour.",
        "Explicit frequency and priority",
        owner.pets,
    )

    # Example 5 — no pet mentioned, falls back to manual assignment notice
    parse_and_assign(
        "Give a quick brushing session, should take around 10 minutes.",
        "No pet mentioned — fallback demo",
        owner.pets,
    )

    # ── Step 5: Build Schedule ────────────────────────────────────────────────
    section("Step 5", "Build Schedule (Priority-Based Algorithm)")

    scheduler = Scheduler(owner=owner, date=date.today())
    scheduler.build_daily_plan()

    print(f"  Owner : {owner.name}  |  "
          f"Date: {date.today().strftime('%A, %B %d %Y')}  |  "
          f"Budget: {owner.available_time_min} min\n")

    print(f"  {'START':^7}  {'END':^7}  {'PET':<10}  {'TASK':<22}  PRIORITY")
    print(f"  {'─'*7}  {'─'*7}  {'─'*10}  {'─'*22}  {'─'*8}")
    for entry in scheduler.sort_by_time():
        print(f"  {entry.start.strftime('%H:%M'):^7}  {entry.end.strftime('%H:%M'):^7}"
              f"  {entry.pet.name:<10}  {entry.task.description:<22}  {entry.task.priority}")

    if scheduler.overflow_tasks:
        print(f"\n  Could Not Fit ({len(scheduler.overflow_tasks)} task(s) exceeded time budget):")
        for t in scheduler.overflow_tasks:
            print(f"    ❌  {t.description:<24}  {t.duration_min} min  [{t.priority}]")

    print()
    conflicts = scheduler.warn_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  ⚠️  {w}")
    else:
        print("  Conflict check: none detected ✅")

    # ── Step 6: Recurrence & Filters ─────────────────────────────────────────
    section("Step 6", "Recurrence & Filters")

    print("  Recurrence check — is each task due today?\n")
    print(f"  {'PET':<10}  {'TASK':<24}  {'FREQUENCY':<8}  STATUS")
    print(f"  {'─'*10}  {'─'*24}  {'─'*8}  {'─'*14}")
    for pet in owner.pets:
        for task in pet.tasks:
            status = "Due today ✅" if task.is_due(date.today()) else "Not due yet ⏳"
            print(f"  {pet.name:<10}  {task.description:<24}  {task.frequency:<8}  {status}")

    print(f"\n  Filter — pending tasks for {buddy.name}:")
    for t in owner.filter_tasks(pet_id=buddy.id, status="pending"):
        print(f"    • {t.description} ({t.priority})")

    daily = next((e for e in scheduler.schedule if e.task.frequency == "daily"), None)
    if daily:
        print(f"\n  Completing '{daily.task.description}' → queuing next occurrence...")
        next_task = scheduler.complete_task(daily.task.id)
        if next_task:
            print(f"    ✅ Next '{next_task.description}' due on "
                  f"{next_task.last_scheduled + timedelta(days=1)}")

    # ── Step 7: AI Schedule Critique ──────────────────────────────────────────
    section("Step 7", "AI Schedule Critique (Agentic Tool-Use Analysis)")

    print("  Claude is reviewing your schedule using tool calls...\n")
    try:
        print(critique_schedule(scheduler, owner))
    except Exception as e:
        print(f"  Critic error: {e}")

    print(f"\n{DIVIDER}")
    print(f"  Demo complete.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
