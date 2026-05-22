from __future__ import annotations

from dataclasses import dataclass, field

from gigavibe.context import trim_messages
from gigavibe.messages import Message
from gigavibe.modes import ChatMode


@dataclass(slots=True)
class ChatSession:
    history: list[Message] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.history.append(Message(role='user', content=content))

    def add_assistant_message(self, content: str) -> None:
        self.history.append(Message(role='assistant', content=content))

    def reset(self) -> None:
        self.history.clear()

    def build_request_messages(self, mode: ChatMode, max_context_tokens: int) -> list[Message]:
        system = Message(role='system', content=mode.system_prompt)
        return trim_messages([system, *self.history], max_context_tokens)
