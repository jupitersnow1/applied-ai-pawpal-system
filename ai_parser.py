"""
PawPal+ AI Parser

This module uses Claude to turn natural language task descriptions
into structured dictionaries that work with the Task class.
Supports single and multi-task descriptions in one prompt.
"""

import os
import json
import logging
import anthropic

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ai_parser] %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_FREQUENCIES = {"daily", "weekly", "once"}


def _validate_task(raw: dict) -> dict:
    """Sanitize and apply safe defaults to a single parsed task dict."""
    description = str(raw.get("description", "")).strip()
    if not description:
        raise ValueError("Task description is empty.")

    try:
        duration_min = int(raw.get("duration_min", 15))
        if duration_min <= 0:
            raise ValueError
    except (ValueError, TypeError):
        log.warning("Invalid duration_min '%s', defaulting to 15.", raw.get("duration_min"))
        duration_min = 15

    priority = raw.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        log.warning("Invalid priority '%s', defaulting to 'medium'.", priority)
        priority = "medium"

    frequency = raw.get("frequency", "daily")
    if frequency not in VALID_FREQUENCIES:
        log.warning("Invalid frequency '%s', defaulting to 'daily'.", frequency)
        frequency = "daily"

    mentioned_raw = raw.get("mentioned_name")
    mentioned_name = str(mentioned_raw).strip() if isinstance(mentioned_raw, str) else None

    return {
        "description": description,
        "duration_min": duration_min,
        "priority": priority,
        "frequency": frequency,
        "mentioned_name": mentioned_name,
    }


def _build_pet_context(pets: list) -> str:
    """Format a registered pet list for inclusion in the parser prompt."""
    lines = []
    for p in pets:
        age_unit = p.preferences.get("age_unit", "years")
        sex = p.preferences.get("sex", "unknown")
        sex_part = f", {sex}" if sex != "unknown" else ""
        lines.append(f"- {p.name} ({p.species}, {p.age} {age_unit} old{sex_part})")
    return "\n".join(lines)


def parse_task_from_text(user_input: str, pets: list | None = None) -> list[dict]:
    """
    Parse one or more pet care tasks from a natural language description.

    pets: optional list of Pet objects. When provided, Claude can resolve
    descriptors like "the dog", "puppy", or "him" to the correct registered name.

    Returns a list of validated task dicts, each with:
        description, duration_min, priority, frequency, mentioned_name.
    Raises ValueError if parsing fails or no valid tasks are found.
    """
    log.info("Parsing input: %s", user_input[:120])

    pet_context_block = ""
    if pets:
        pet_context_block = f"""
Registered pets in this owner's account:
{_build_pet_context(pets)}

When a descriptor like "the dog", "puppy", "kitten", "the cat", "him", "her", or "he"/"she"
is used and exactly one registered pet matches that description, set mentioned_name to that
pet's exact registered name. Use sex to resolve "him"/"his"/"he" (male) and "her"/"she" (female).
Use age to resolve "puppy" (dog under 1 year) or "kitten" (cat under 1 year).
If the descriptor is ambiguous (matches multiple pets), set mentioned_name to null.
"""

    prompt = f"""You are a helpful assistant for a pet care scheduling app.
{pet_context_block}
Parse the following natural language description into a JSON array of task objects.
- If multiple tasks are described, return one object per task.
- If only one task is described, return an array with a single object.

Each object must have exactly these fields:
- "description": a short action-only task name — do NOT include the pet's name (e.g. "morning walk", "feeding", "grooming session")
- "duration_min": an integer number of minutes (default 15 if not mentioned)
- "priority": one of exactly "low", "medium", or "high" (default "medium")
- "frequency": one of exactly "daily", "weekly", or "once" (default "daily")
- "mentioned_name": the exact registered pet name, or null if no pet was mentioned or the reference is ambiguous

Respond with ONLY a valid JSON array — no explanation, no markdown, no extra text.

Task description: "{user_input}"
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    log.info("Raw response: %s", raw[:300])

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw.strip())

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        raise ValueError(f"Unexpected response shape from Claude: {type(data)}")

    validated = []
    for item in data:
        try:
            validated.append(_validate_task(item))
        except ValueError as e:
            log.warning("Skipping invalid task item: %s | error: %s", item, e)

    if not validated:
        raise ValueError("No valid tasks could be parsed from the input.")

    log.info("Parsed %d task(s) successfully.", len(validated))
    return validated
