from __future__ import annotations

import os
from dataclasses import dataclass, replace


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'y', 'да'}


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class AppConfig:
    provider: str = 'mock'
    model: str = 'GigaChat'
    max_context_tokens: int = 3500
    temperature: float = 0.7
    api_url: str = 'https://api.openai.com/v1/chat/completions'
    api_key: str | None = None
    gigachat_credentials: str | None = None
    gigachat_verify_ssl_certs: bool = True

    @classmethod
    def from_env(cls) -> AppConfig:
        return cls(
            provider=os.getenv('LLM_PROVIDER', 'mock').strip().lower(),
            model=os.getenv('LLM_MODEL', 'GigaChat').strip() or 'GigaChat',
            max_context_tokens=_parse_int(os.getenv('LLM_MAX_CONTEXT_TOKENS'), 3500),
            temperature=_parse_float(os.getenv('LLM_TEMPERATURE'), 0.7),
            api_url=os.getenv(
                'LLM_API_URL',
                'https://api.openai.com/v1/chat/completions',
            ).strip(),
            api_key=os.getenv('LLM_API_KEY'),
            gigachat_credentials=os.getenv('GIGACHAT_CREDENTIALS'),
            gigachat_verify_ssl_certs=_parse_bool(
                os.getenv('GIGACHAT_VERIFY_SSL_CERTS'),
                True,
            ),
        )

    def with_overrides(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        max_context_tokens: int | None = None,
    ) -> AppConfig:
        return replace(
            self,
            provider=provider or self.provider,
            model=model or self.model,
            max_context_tokens=max_context_tokens or self.max_context_tokens,
        )
