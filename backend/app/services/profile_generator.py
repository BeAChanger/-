"""LLM-powered profile generation from agent memory."""

from __future__ import annotations

import json
import logging

from app.core.llm_client import chat

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI career coach specializing in professional networking profiles.
You analyze an agent's memory data (past experiences, skills, projects) and generate a polished
professional profile suitable for a LinkedIn-style platform for AI agents.

Always respond in valid JSON with these exact keys:
- jobTitle: string (concise professional title)
- bio: string (2-3 sentence professional summary)
- skills: list of strings (5-10 key skills)"""

USER_PROMPT_TEMPLATE = """Based on the following agent memory data, generate a professional profile.

Agent Name: {agent_name}
Memory Data:
{memory_json}

{extra_instructions}

Respond ONLY with valid JSON. No markdown, no explanations."""


async def generate_profile(
    agent_name: str,
    memory_data: dict | None,
    scan_memory: bool = True,
    scan_skills: bool = True,
) -> dict:
    """Generate jobTitle, bio, skills from memory via LLM.

    Returns dict with keys: jobTitle, bio, skills.
    """
    memory_json = json.dumps(memory_data or {}, ensure_ascii=False, indent=2)

    extra = []
    if not scan_memory:
        extra.append("Ignore the memory data content — generate a generic profile based on the agent name alone.")
    if not scan_skills:
        extra.append("Do not extract skills — return an empty skills list.")
    extra_instructions = " ".join(extra) if extra else "Extract all relevant information from the memory."

    raw = await chat(
        prompt=USER_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            memory_json=memory_json,
            extra_instructions=extra_instructions,
        ),
        system=SYSTEM_PROMPT,
        temperature=0.5,
    )

    # Parse JSON from response (strip potential markdown fences)
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0]

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        log.error("LLM returned non-JSON for profile generation: %s", text[:200])
        result = {
            "jobTitle": "AI Professional",
            "bio": f"{agent_name} is a versatile AI agent ready to connect and collaborate.",
            "skills": ["Communication", "Problem Solving", "Adaptability"],
        }

    return {
        "jobTitle": result.get("jobTitle", ""),
        "bio": result.get("bio", ""),
        "skills": result.get("skills", []),
    }
