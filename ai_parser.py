"""
PawPal+ AI Parser

This module uses Claude to turn natural language task descriptions
into structured dictionaries that work with the Task class.
"""

import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def parse_task_from_text(user_input: str) -> dict:
    """
    Takes a user's task description in plain English and sends it to Claude,
    which converts it into a structured format we can use.

    Returns a dict with: 
        -   description 
        -   duration_min 
        -   priority
        -   frequency.
    Returns None if parsing fails.
    """
    prompt = f"""You are a helpful assistant for a pet care scheduling app.

Parse the following natural language task description into a structured JSON object.

Rules:
- "description": a short, clear task name (e.g. "morning walk")
- "duration_min": an integer number of minutes (default 15 if not mentioned)
- "priority": one of exactly "low", "medium", or "high" (default "medium")
- "frequency": one of exactly "daily", "weekly", or "once" (default "daily")

Respond with ONLY a valid JSON object — no explanation, no markdown, no extra text.

Task description: "{user_input}"
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # strip markdown code fences if claude wraps the response
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
