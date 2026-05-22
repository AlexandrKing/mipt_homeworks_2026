from __future__ import annotations

from math import ceil

from gigavibe.messages import Message

CHARS_PER_TOKEN_APPROX = 3.0


def estimate_tokens(text: str) -> int:
    """Very rough token estimate without third-party tokenizers.

    It is intentionally conservative for Russian text. Real providers may expose
    an exact token counting endpoint; this project keeps a lightweight local
    approximation so old messages can still be trimmed before each request.
    """

    if not text:
        return 0
    return max(1, ceil(len(text) / CHARS_PER_TOKEN_APPROX))


def message_tokens(message: Message) -> int:
    # A small overhead accounts for role names and chat message delimiters.
    return estimate_tokens(message.content) + 4


def messages_tokens(messages: list[Message]) -> int:
    return sum(message_tokens(message) for message in messages)


def trim_messages(messages: list[Message], max_tokens: int) -> list[Message]:
    """Keep the system prompt and the newest dialogue messages within a budget.

    If the dialogue becomes too long, the oldest non-system messages are removed,
    which mirrors the context-window explanation from the task statement.
    """

    if max_tokens <= 0:
        raise ValueError('max_tokens must be positive')
    if not messages:
        return []

    system_message: Message | None = None
    history = messages
    if messages[0].role == 'system':
        system_message = messages[0]
        history = messages[1:]

    result_reversed: list[Message] = []
    used_tokens = message_tokens(system_message) if system_message is not None else 0

    for message in reversed(history):
        current_tokens = message_tokens(message)
        if used_tokens + current_tokens <= max_tokens:
            result_reversed.append(message)
            used_tokens += current_tokens
        elif not result_reversed:
            # The newest message is too large. Keep a shortened tail so the model
            # still sees the user's latest request.
            available = max(1, max_tokens - used_tokens - 4)
            max_chars = max(1, int(available * CHARS_PER_TOKEN_APPROX))
            shortened = Message(
                role=message.role,
                content='[...начало сообщения обрезано...]\n' + message.content[-max_chars:],
            )
            result_reversed.append(shortened)
            break

    trimmed_history = list(reversed(result_reversed))
    if system_message is None:
        return trimmed_history
    return [system_message, *trimmed_history]
