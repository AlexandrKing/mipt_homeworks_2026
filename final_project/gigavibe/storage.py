from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gigavibe.messages import Message
from gigavibe.modes import DEFAULT_MODE, get_mode

DEFAULT_HISTORY_FILE = Path('.gigavibe_history.json')


def save_history(path: Path, mode_name: str, history: list[Message]) -> None:
    data = {
        'mode': mode_name,
        'history': [message.to_dict() for message in history],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load_history(path: Path) -> tuple[str, list[Message]]:
    if not path.exists():
        return DEFAULT_MODE, []

    raw = path.read_text(encoding='utf-8')
    data: dict[str, Any] = json.loads(raw)
    mode_name = str(data.get('mode') or DEFAULT_MODE)
    get_mode(mode_name)  # validate saved mode

    raw_history = data.get('history', [])
    if not isinstance(raw_history, list):
        raise ValueError('Saved history must contain a list')

    history = [Message.from_dict(item) for item in raw_history]
    return mode_name, history
