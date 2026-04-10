"""Ollama LLM service – local AI for content classification and organization."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import requests

from config import OllamaConfig

log = logging.getLogger(__name__)


# ─── Low-level helpers ───────────────────────────────────────────────────────

def _call_ollama(prompt: str, system: str = "", model: str | None = None) -> str:
    """
    Call the Ollama REST API and return the model's text response.
    Tries the configured model first, then falls back to alternatives.
    """
    models_to_try = [model or OllamaConfig.MODEL] + OllamaConfig.FALLBACK_MODELS
    tried: list[str] = []

    for m in models_to_try:
        if m in tried:
            continue
        tried.append(m)
        payload: dict[str, Any] = {
            "model": m,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        try:
            resp = requests.post(
                f"{OllamaConfig.HOST}/api/generate",
                json=payload,
                timeout=OllamaConfig.TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.exceptions.ConnectionError:
            log.warning("Ollama not reachable at %s", OllamaConfig.HOST)
            return (
                f"⚠️ **Ollama is not running.** Please start Ollama with `ollama serve` "
                f"and make sure the model is pulled (`ollama pull {m}`)."
            )
        except Exception as exc:  # noqa: BLE001
            log.warning("Ollama error with model %s: %s", m, exc)
            continue

    return "⚠️ Could not reach Ollama with any configured model."


def list_ollama_models() -> list[str]:
    """Return list of locally available Ollama models."""
    try:
        resp = requests.get(f"{OllamaConfig.HOST}/api/tags", timeout=10)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:  # noqa: BLE001
        return []


# ─── Research-specific prompts ───────────────────────────────────────────────

_CLASSIFY_SYSTEM = """You are a research assistant specialized in organizing academic content.
You must respond ONLY with valid JSON.
No markdown, no code blocks, just raw JSON."""

_CLASSIFY_PROMPT_TPL = """Given the research topic: "{topic}"

Analyze this content and classify it into hierarchical themes:
- MACRO: broad overarching themes (2-4 items)
- MESO: intermediate sub-themes (4-8 items)
- MICRO: specific details and findings (6-12 items)

Also extract:
- content_type: one of ["patent", "article", "web_page", "news", "other"]
- key_concepts: list of 5-10 key terms
- relevance_score: integer 0-100 (how relevant to the topic)
- summary: resumo em português (2-3 frases)

Content title: {title}
Content text (truncated):
{text}

Return ONLY valid JSON matching this structure:
{{
  "content_type": "...",
  "relevance_score": 0,
  "summary": "...",
  "key_concepts": [],
  "themes": {{
    "macro": [],
    "meso": [],
    "micro": []
  }}
}}"""


def classify_content(text: str, title: str, topic: str) -> dict[str, Any]:
    """
    Use Ollama to classify content into macro/meso/micro themes.
    Returns a dict with classification results.
    """
    truncated = text[:4000] if len(text) > 4000 else text
    prompt = _CLASSIFY_PROMPT_TPL.format(
        topic=topic,
        title=title,
        text=truncated,
    )
    raw = _call_ollama(prompt, system=_CLASSIFY_SYSTEM)

    # If Ollama is unavailable, return an error dict
    if raw.startswith("⚠️"):
        return {"error": raw, "themes": {"macro": [], "meso": [], "micro": []}}

    # Extract JSON from the response (handle markdown code blocks if present)
    json_str = raw.strip()
    if "```" in json_str:
        json_str = json_str.split("```")[1]
        if json_str.startswith("json"):
            json_str = json_str[4:]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        log.warning("LLM returned non-JSON: %s", raw[:200])
        return {
            "error": "LLM returned non-JSON response",
            "raw": raw[:500],
            "themes": {"macro": [], "meso": [], "micro": []},
        }


_CAMUS_PERSONA_PT = """Você é Botersson, um assistente de pesquisa com personalidade inspirada em Albert Camus:
claro, humano, lúcido, reflexivo e direto. Evite dramatização e jargão excessivo.
Sempre responda em português (pt-BR), mesmo que a pergunta venha em outro idioma."""

_SUMMARY_SYSTEM = (
    f"{_CAMUS_PERSONA_PT}\n"
    "Você é um resumidor acadêmico conciso. Entregue sínteses claras e bem estruturadas."
)


def summarize_content(text: str, max_words: int = 200) -> str:
    """Summarize content using the LLM."""
    truncated = text[:6000] if len(text) > 6000 else text
    prompt = (
        f"Summarize the following text in at most {max_words} words. "
        f"Focus on the main findings and contributions:\n\n{truncated}"
    )
    return _call_ollama(prompt, system=_SUMMARY_SYSTEM)


_COMPARE_SYSTEM = (
    f"{_CAMUS_PERSONA_PT}\n"
    "Você é um analista de pesquisa experiente. Compare fontes com objetividade."
)


def compare_sources(sources: list[dict[str, Any]], topic: str) -> str:
    """Ask the LLM to compare multiple research sources."""
    formatted = "\n\n".join(
        f"[{i+1}] {s.get('title','Untitled')}: {s.get('text','')[:500]}"
        for i, s in enumerate(sources)
    )
    prompt = (
        f"Topic: {topic}\n\n"
        f"Compare and contrast these {len(sources)} sources regarding the topic above. "
        f"Identify agreements, contradictions, and research gaps:\n\n{formatted}"
    )
    return _call_ollama(prompt, system=_COMPARE_SYSTEM)


def answer_question(question: str, context: str) -> str:
    """Answer a user question based on scraped context."""
    clean_context = context.strip()
    prompt = (
        f"Responda à pergunta do usuário: {question}\n\n"
        f"Contexto (pode estar vazio):\n{clean_context[:5000]}"
    )
    return _call_ollama(prompt, system=_CAMUS_PERSONA_PT)


# ─── Async wrappers ──────────────────────────────────────────────────────────

async def async_classify(text: str, title: str, topic: str) -> dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, classify_content, text, title, topic)


async def async_summarize(text: str, max_words: int = 200) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, summarize_content, text, max_words)


async def async_compare(sources: list[dict[str, Any]], topic: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, compare_sources, sources, topic)


async def async_answer(question: str, context: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, answer_question, question, context)
