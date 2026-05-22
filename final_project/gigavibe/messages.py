from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Role = Literal['system', 'user', 'assistant']
VALID_ROLES = ('system', 'user', 'assistant')


@dataclass(slots=True)
class Message:
    """A single message in the LLM conversation history."""

    role: Role
    content: str

    def __post_init__(self) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f'Unsupported message role: {self.role!r}')
        if not isinstance(self.content, str):
            raise TypeError('Message content must be a string')

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role, 'content': self.content}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        role = data.get('role')
        content = data.get('content')
        if role == 'system':
            parsed_role: Role = role
        elif role == 'user':
            parsed_role = role
        elif role == 'assistant':
            parsed_role = role
        else:
            raise ValueError(f'Unsupported message role in saved history: {role!r}')
        if not isinstance(content, str):
            raise ValueError('Saved history message content must be a string')
        return cls(role=parsed_role, content=content)
