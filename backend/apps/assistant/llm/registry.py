from dataclasses import dataclass
from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import LLMProvider


@dataclass(frozen=True)
class ProviderDefaults:
    model: str
    max_tokens: int  # per reply


# Used when LLM_MODEL / LLM_MAX_TOKENS aren't set in the environment.
DEFAULTS = {
    # Free tier: small reply cap so requests fit the shared per-minute token budget.
    "groq": ProviderDefaults(model="openai/gpt-oss-120b", max_tokens=3000),
    "anthropic": ProviderDefaults(model="claude-opus-5-5", max_tokens=16000),
    "fake": ProviderDefaults(model="kafka-offline-demo", max_tokens=1000),
}


def _defaults() -> ProviderDefaults:
    try:
        return DEFAULTS[settings.LLM_PROVIDER]
    except KeyError:
        raise ImproperlyConfigured(
            f"Unknown LLM_PROVIDER {settings.LLM_PROVIDER!r}; use one of: {', '.join(DEFAULTS)}."
        ) from None


def max_reply_tokens() -> int:
    return settings.LLM_MAX_TOKENS or _defaults().max_tokens


@lru_cache(maxsize=1)
def get_provider() -> LLMProvider:
    """The configured provider (one shared, thread-safe client per process)."""
    name = settings.LLM_PROVIDER
    model = settings.LLM_MODEL or _defaults().model  # _defaults() rejects unknown names
    if name == "groq":
        from .groq_provider import GroqProvider

        return GroqProvider(model=model, effort=settings.LLM_EFFORT, timeout=settings.LLM_TIMEOUT)
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(model=model, effort=settings.LLM_EFFORT, timeout=settings.LLM_TIMEOUT)
    from .fake_provider import FakeProvider

    return FakeProvider(model=model, delay=settings.LLM_FAKE_DELAY)
