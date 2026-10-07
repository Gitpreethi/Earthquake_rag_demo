"""LLM providers behind one small interface.

* anthropic  – Claude via the Anthropic API (ANTHROPIC_API_KEY)
* openai     – any OpenAI-compatible chat endpoint (OpenAI, Ollama, vLLM, LM Studio ...)
               via OPENAI_BASE_URL / OPENAI_API_KEY / LLM_MODEL
* extractive – no LLM: returns the most relevant evidence sentences verbatim
               (keeps the prototype usable offline; clearly labelled in the UI)
"""
from __future__ import annotations

import logging
from functools import lru_cache

import httpx

from ..config import settings

log = logging.getLogger(__name__)


class LLMError(RuntimeError):
    pass


class BaseLLM:
    provider = "base"
    model = ""
    is_generative = True

    def complete(self, system: str, user: str, max_tokens: int | None = None) -> str:  # pragma: no cover
        raise NotImplementedError

    def describe(self) -> dict:
        return {"provider": self.provider, "model": self.model, "generative": self.is_generative}


class AnthropicLLM(BaseLLM):
    provider = "anthropic"

    def __init__(self) -> None:
        import anthropic

        self.model = settings.llm_model or "claude-sonnet-5-5"
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def complete(self, system: str, user: str, max_tokens: int | None = None) -> str:
        try:
            msg = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens or settings.llm_max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as e:  # network / auth / model errors
            raise LLMError(f"Anthropic API error: {e}") from e
        return "".join(getattr(b, "text", "") for b in msg.content)


class OpenAICompatibleLLM(BaseLLM):
    provider = "openai"

    def __init__(self) -> None:
        if not settings.llm_model:
            raise LLMError("LLM_MODEL must be set for the OpenAI-compatible provider")
        self.model = settings.llm_model
        self.base_url = (settings.openai_base_url or "https://api.openai.com/v1").rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.openai_api_key}"} if settings.openai_api_key else {}

    def complete(self, system: str, user: str, max_tokens: int | None = None) -> str:
        body = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": max_tokens or settings.llm_max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        try:
            r = httpx.post(f"{self.base_url}/chat/completions", json=body, headers=self.headers, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"OpenAI-compatible endpoint error: {e}") from e


class ExtractiveLLM(BaseLLM):
    """Not a language model: signals the RAG layer to build an extractive answer."""

    provider = "extractive"
    model = "none (evidence sentences only)"
    is_generative = False

    def complete(self, system: str, user: str, max_tokens: int | None = None) -> str:  # pragma: no cover
        raise LLMError("Extractive mode does not generate text")


def make_llm(provider: str | None = None) -> BaseLLM:
    p = (provider or settings.llm_provider or "auto").lower()
    if p == "auto":
        if settings.anthropic_api_key:
            p = "anthropic"
        elif settings.openai_base_url or settings.openai_api_key:
            p = "openai"
        else:
            p = "extractive"
    if p == "anthropic":
        return AnthropicLLM()
    if p == "openai":
        return OpenAICompatibleLLM()
    return ExtractiveLLM()


@lru_cache(maxsize=1)
def get_llm() -> BaseLLM:
    llm = make_llm()
    log.info("LLM provider: %s", llm.describe())
    return llm
