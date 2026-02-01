"""
Keywords AI gateway client and telemetry setup.

All LLM calls are routed through the Keywords AI gateway for:
- Centralized logging and observability
- Managed prompt versioning
- Tracing of agent workflows

Requires env vars:
  KEYWORDS_AI_API_KEY   - Your Keywords AI API key
  KEYWORDSAI_BASE_URL   - Gateway base URL (default: https://api.keywordsai.co/api)
  BBOX_DETECTOR_PROMPT_ID - Prompt ID for the detection prompt
  BBOX_JUDGE_PROMPT_ID    - Prompt ID for the judge prompt
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger("geomarble.keywords_client")

# ---------------------------------------------------------------------------
# Telemetry singleton
# ---------------------------------------------------------------------------
_telemetry = None


def init_telemetry():
    """Initialise Keywords AI tracing. Call once at app startup."""
    global _telemetry
    if _telemetry is not None:
        return _telemetry
    try:
        from keywordsai_tracing.main import KeywordsAITelemetry
        _telemetry = KeywordsAITelemetry()
        logger.info("Keywords AI telemetry initialised")
    except Exception as e:
        logger.warning(f"Keywords AI telemetry init failed (tracing disabled): {e}")
    return _telemetry


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    key = os.environ.get("KEYWORDS_AI_API_KEY", "")
    if not key:
        raise RuntimeError("KEYWORDS_AI_API_KEY env var is not set")
    return key


def _get_base_url() -> str:
    return os.environ.get("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")


def get_detector_prompt_id() -> str | None:
    """Return detector prompt ID, or None if not configured (inline prompt will be used)."""
    return os.environ.get("BBOX_DETECTOR_PROMPT_ID", "").strip() or None


def get_judge_prompt_id() -> str | None:
    """Return judge prompt ID, or None if not configured (inline prompt will be used)."""
    return os.environ.get("BBOX_JUDGE_PROMPT_ID", "").strip() or None


# ---------------------------------------------------------------------------
# Gateway call
# ---------------------------------------------------------------------------

async def call_gateway(
    *,
    messages: list[dict],
    prompt_id: str | None = None,
    variables: dict[str, str] | None = None,
    model: str = "gpt-5.2",
    temperature: float = 0.1,
    max_tokens: int = 1000,
    call_type: str = "detect",
) -> dict[str, Any]:
    """
    Make a chat completion call through the Keywords AI gateway.

    If prompt_id is provided, uses managed prompts with variables.
    Otherwise sends messages as-is (inline prompt mode).

    Returns a dict with:
      - response_text: the assistant's message content
      - tokens_in: prompt token count
      - tokens_out: completion token count
      - latency_ms: round-trip time in milliseconds
      - model: model used
      - prompt_id: prompt ID used (or "inline")
      - call_type: "detect" or "judge"
      - status: "success" or "error"
      - error: error message (only on failure)
    """
    api_key = _get_api_key()
    base_url = _get_base_url()
    url = f"{base_url}/chat/completions"

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if prompt_id:
        body["prompt"] = {
            "prompt_id": prompt_id,
            "variables": variables or {},
            "override": True,
        }

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = round((time.perf_counter() - start) * 1000)

        usage = data.get("usage", {})
        response_text = data["choices"][0]["message"]["content"]

        pid_label = prompt_id or "inline"
        return {
            "response_text": response_text,
            "tokens_in": usage.get("prompt_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0),
            "latency_ms": elapsed_ms,
            "model": model,
            "prompt_id": pid_label,
            "call_type": call_type,
            "status": "success",
        }

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.error(f"Gateway call failed ({call_type}): {e}")
        pid_label = prompt_id or "inline"
        return {
            "response_text": "",
            "tokens_in": 0,
            "tokens_out": 0,
            "latency_ms": elapsed_ms,
            "model": model,
            "prompt_id": pid_label,
            "call_type": call_type,
            "status": "error",
            "error": str(e),
        }
