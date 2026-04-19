"""
PawPal+ Schedule Critic Agent

Uses Claude Sonnet with tool use to analyze a generated schedule and return
a structured, per-pet critique with a final summary. Claude actively calls
tools to gather schedule data rather than receiving it all at once.
"""

import os
import logging
import anthropic
from pawpal_system import Scheduler, Owner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [schedule_critic] %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TOOLS = [
    {
        "name": "get_scheduled_tasks",
        "description": "Returns all tasks successfully scheduled for today, grouped by pet.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_overflow_tasks",
        "description": "Returns tasks that could not fit in today's schedule due to time constraints.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_conflict_warnings",
        "description": "Returns any time overlap warnings between scheduled tasks.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_pet_summary",
        "description": "Returns a detailed breakdown of scheduled and pending tasks for one specific pet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pet_id": {
                    "type": "string",
                    "description": "The ID of the pet to summarize (e.g. 'pet1')",
                }
            },
            "required": ["pet_id"],
        },
    },
]


def _run_tool(name: str, inputs: dict, scheduler: Scheduler, owner: Owner) -> str:
    log.info("Tool called: %s | inputs: %s", name, inputs)

    if name == "get_scheduled_tasks":
        if not scheduler.schedule:
            return "No tasks were scheduled today."
        lines = []
        for entry in scheduler.sort_by_time():
            pet_name = entry.pet.name if entry.pet else "Unknown"
            lines.append(
                f"{pet_name} | {entry.task.description} | {entry.task.priority} priority"
                f" | {entry.task.duration_min} min"
                f" | {entry.start.strftime('%H:%M')}–{entry.end.strftime('%H:%M')}"
            )
        return "\n".join(lines)

    if name == "get_overflow_tasks":
        if not scheduler.overflow_tasks:
            return "No overflow — all tasks fit within the available time."
        return "\n".join(
            f"{t.description} ({t.priority} priority, {t.duration_min} min)"
            for t in scheduler.overflow_tasks
        )

    if name == "get_conflict_warnings":
        warnings = scheduler.warn_conflicts()
        return "\n".join(warnings) if warnings else "No conflicts detected."

    if name == "get_pet_summary":
        pet_id = inputs.get("pet_id", "")
        pet = next((p for p in owner.pets if p.id == pet_id), None)
        if not pet:
            return f"No pet found with id '{pet_id}'."
        scheduled = [e for e in scheduler.schedule if e.pet and e.pet.id == pet_id]
        overflow = [t for t in scheduler.overflow_tasks if t in pet.tasks]
        pending_unscheduled = [
            t for t in pet.get_pending_tasks()
            if t not in [e.task for e in scheduled] and t not in overflow
        ]
        lines = [
            f"Pet: {pet.name} ({pet.species}, age {pet.age})",
            f"Scheduled today: {len(scheduled)} task(s)",
        ]
        for e in scheduled:
            lines.append(
                f"  ✅ {e.task.description} — {e.task.priority} priority,"
                f" {e.task.duration_min} min,"
                f" {e.start.strftime('%H:%M')}–{e.end.strftime('%H:%M')}"
            )
        if overflow:
            lines.append(f"Cut (didn't fit): {len(overflow)} task(s)")
            for t in overflow:
                lines.append(f"  ❌ {t.description} — {t.priority} priority, {t.duration_min} min")
        if pending_unscheduled:
            lines.append(f"Pending but not yet due: {len(pending_unscheduled)} task(s)")
            for t in pending_unscheduled:
                lines.append(f"  ⏳ {t.description}")
        return "\n".join(lines)

    return f"Unknown tool: {name}"


def critique_schedule(scheduler: Scheduler, owner: Owner) -> str:
    """
    Runs the agentic critique loop. Claude calls tools to gather schedule
    data, then returns a structured per-pet critique with a final summary.
    """
    if not scheduler.schedule and not scheduler.overflow_tasks:
        return "No schedule data to critique. Build a plan first."

    pet_list = ", ".join(f"{p.name} (id: {p.id})" for p in owner.pets)
    log.info(
        "Starting critique for owner '%s' | pets: %s | scheduled: %d | overflow: %d",
        owner.name,
        pet_list,
        len(scheduler.schedule),
        len(scheduler.overflow_tasks),
    )

    system_prompt = f"""You are a friendly pet care scheduling assistant reviewing today's plan for {owner.name}.

Pets in this household: {pet_list}
Available time today: {owner.available_time_min} minutes

Use the available tools to gather information about each pet and the overall schedule,
then write a structured critique using this EXACT format:

---

## 🐾 Schedule Review for {owner.name}

### [species emoji] [Pet Name]
- One bullet per observation — be specific about times, priorities, and durations
- Flag high-priority tasks that were cut, back-to-back overload, or missing care
- Praise good scheduling where it applies

(one section per pet)

### ⚠️ Conflicts & Warnings
- List any time conflicts or say "None detected ✅"

### 📋 Summary
2–3 friendly sentences covering overall plan quality and your top recommendation.

---

Be warm and helpful. Call get_pet_summary for every pet before writing their section."""

    messages = [
        {"role": "user", "content": "Please analyze today's schedule and give me your critique."}
    ]

    # Agentic tool-use loop
    for step in range(10):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )
        log.info("Step %d | stop_reason: %s", step + 1, response.stop_reason)

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    log.info("Critique complete (%d chars)", len(block.text))
                    return block.text
            return "No critique generated."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _run_tool(block.name, block.input, scheduler, owner)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            log.warning("Unexpected stop_reason: %s", response.stop_reason)
            break

    return "Critique could not be completed — agent loop limit reached."
