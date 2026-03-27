"""OpenAI-compatible LLM client (simplified)."""

import logging

import httpx

from app.config import settings

log = logging.getLogger(__name__)

_TIMEOUT = 60.0


async def chat(
    prompt: str,
    system: str = "You are a helpful professional networking assistant.",
    temperature: float = 0.7,
) -> str:
    """Send a single chat completion request, return the assistant message text."""
    if not settings.OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set — returning placeholder")
        return "[LLM unavailable: OPENAI_API_KEY not configured]"

    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
