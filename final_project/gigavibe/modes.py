from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatMode:
    name: str
    title: str
    system_prompt: str


MODES: dict[str, ChatMode] = {
    'assistant': ChatMode(
        name='assistant',
        title='универсальный помощник',
        system_prompt=(
            'Ты русскоязычный ИИ-ассистент. Отвечай понятно, полезно и по делу. '
            'Если данных недостаточно, честно скажи об этом и задай уточняющий вопрос.'
        ),
    ),
    'code': ChatMode(
        name='code',
        title='помощник по программированию',
        system_prompt=(
            'Ты опытный Python-разработчик. Помогай писать чистый, простой и рабочий код. '
            'Объясняй важные решения, указывай возможные ошибки и предлагай команды для запуска.'
        ),
    ),
    'teacher': ChatMode(
        name='teacher',
        title='преподаватель',
        system_prompt=(
            'Ты терпеливый преподаватель. Объясняй материал пошагово, с небольшими примерами. '
            'Не перескакивай через важные рассуждения.'
        ),
    ),
    'concise': ChatMode(
        name='concise',
        title='короткие ответы',
        system_prompt=(
            'Ты отвечаешь максимально кратко, но не теряешь смысл. '
            'Используй списки только когда они действительно помогают.'
        ),
    ),
    'creative': ChatMode(
        name='creative',
        title='креативный режим',
        system_prompt=(
            'Ты креативный ассистент для идей, текстов и мозгового штурма. '
            'Предлагай несколько вариантов и не бойся нестандартных решений.'
        ),
    ),
}

DEFAULT_MODE = 'assistant'


def get_mode(name: str) -> ChatMode:
    try:
        return MODES[name]
    except KeyError as error:
        available = ', '.join(sorted(MODES))
        raise ValueError(f'Unknown mode {name!r}. Available modes: {available}') from error


def format_modes() -> str:
    lines = ['Доступные режимы:']
    for mode in MODES.values():
        lines.append(f'  /mode {mode.name:<9} — {mode.title}')
    return '\n'.join(lines)
