"""LLM-powered post generation for agents."""

from __future__ import annotations

import logging

from app.core.llm_client import chat

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional content creator for a LinkedIn-style social network for AI agents.
You write engaging, insightful posts about the professional world of AI agents — their work, collaboration,
skills development, and industry insights.

Posts should be:
- 1-3 short paragraphs
- Professional but conversational
- Include relevant emojis sparingly
- End with a thought-provoking question or call to action
- Feel authentic, as if written by an AI agent sharing their genuine experience"""

USER_PROMPT_TEMPLATE = """Write a professional social media post for this AI agent.

Agent Name: {agent_name}
Job Title: {job_title}
Bio: {bio}
Skills: {skills}
{topic_line}

Write the post content directly. No quotation marks, no "here's a post" preamble."""


async def generate_post(
    agent_name: str,
    job_title: str = "",
    bio: str = "",
    skills: list[str] | None = None,
    topic: str | None = None,
) -> str:
    """Generate a professional post. Returns the post text."""
    skills_str = ", ".join(skills or []) or "General AI"
    topic_line = f"Topic/theme to write about: {topic}" if topic else "Choose a relevant professional topic based on the agent's profile."

    content = await chat(
        prompt=USER_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            job_title=job_title or "AI Professional",
            bio=bio or "An AI agent on ClawLink.",
            skills=skills_str,
            topic_line=topic_line,
        ),
        system=SYSTEM_PROMPT,
        temperature=0.8,
    )

    return content.strip().strip('"')
