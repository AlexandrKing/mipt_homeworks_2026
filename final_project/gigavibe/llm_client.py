from __future__ import annotations

import json
import textwrap
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

from gigavibe.config import AppConfig
from gigavibe.messages import Message


class LLMClientError(RuntimeError):
    """Raised when an LLM provider cannot return a valid answer."""


class LLMClient(ABC):
    @abstractmethod
    def complete(self, messages: list[Message], config: AppConfig) -> str:
        """Return an assistant answer for the given chat messages."""


class MockLLMClient(LLMClient):
    """Offline deterministic client for demos and tests."""

    def complete(self, messages: list[Message], config: AppConfig) -> str:
        last_user = next(
            (message.content for message in reversed(messages) if message.role == 'user'),
            '',
        )
        return textwrap.dedent(
            f"""
            Я работаю в offline/mock-режиме, поэтому не отправляю запрос во внешнюю LLM.

            Последний запрос пользователя: {last_user!r}

            Чтобы подключить реальную модель, задайте LLM_PROVIDER=gigachat или LLM_PROVIDER=openai
            и укажите нужные переменные окружения. Напишите /help для списка команд.
            """
        ).strip()


class OpenAICompatibleClient(LLMClient):
    """Client for OpenAI-compatible /chat/completions endpoints."""

    def complete(self, messages: list[Message], config: AppConfig) -> str:
        if not config.api_key:
            raise LLMClientError('LLM_API_KEY is not set')

        payload = {
            'model': config.model,
            'messages': [message.to_dict() for message in messages],
            'temperature': config.temperature,
            'stream': False,
        }
        body = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            url=config.api_url,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                response_body = response.read().decode('utf-8')
        except urllib.error.HTTPError as error:
            details = error.read().decode('utf-8', errors='replace')
            raise LLMClientError(f'HTTP {error.code}: {details}') from error
        except urllib.error.URLError as error:
            raise LLMClientError(f'Network error: {error}') from error

        try:
            data: dict[str, Any] = json.loads(response_body)
            return str(data['choices'][0]['message']['content'])
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise LLMClientError(f'Unexpected provider response: {response_body[:500]}') from error


class GigaChatSDKClient(LLMClient):
    """Client based on the official gigachat Python package."""

    def complete(self, messages: list[Message], config: AppConfig) -> str:
        if not config.gigachat_credentials:
            raise LLMClientError('GIGACHAT_CREDENTIALS is not set')

        try:
            from gigachat import GigaChat  # type: ignore[import-not-found]
            from gigachat.models import Chat, Messages  # type: ignore[import-not-found]
        except ImportError as error:
            raise LLMClientError(
                "The 'gigachat' package is not installed. Run: pip install gigachat",
            ) from error

        sdk_messages = [
            Messages(role=message.role, content=message.content) for message in messages
        ]
        chat = Chat(
            model=config.model,
            messages=sdk_messages,
            temperature=config.temperature,
        )

        try:
            with GigaChat(
                credentials=config.gigachat_credentials,
                verify_ssl_certs=config.gigachat_verify_ssl_certs,
            ) as client:
                response = client.chat(chat)
        except Exception as error:  # SDK can raise different provider-specific errors.
            raise LLMClientError(str(error)) from error

        try:
            return str(response.choices[0].message.content)
        except (AttributeError, IndexError, TypeError) as error:
            raise LLMClientError(f'Unexpected GigaChat SDK response: {response!r}') from error


def create_client(provider: str) -> LLMClient:
    provider = provider.strip().lower()
    if provider == 'mock':
        return MockLLMClient()
    if provider in {'openai', 'openai-compatible', 'compatible'}:
        return OpenAICompatibleClient()
    if provider == 'gigachat':
        return GigaChatSDKClient()
    raise ValueError('Unknown LLM provider. Use one of: mock, gigachat, openai')
