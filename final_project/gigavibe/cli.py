from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from gigavibe.config import AppConfig
from gigavibe.context import messages_tokens
from gigavibe.llm_client import LLMClientError, create_client
from gigavibe.modes import DEFAULT_MODE, format_modes, get_mode
from gigavibe.session import ChatSession
from gigavibe.storage import DEFAULT_HISTORY_FILE, load_history, save_history

HELP_TEXT = """
Команды:
  /help                 показать справку
  /mode                 показать режимы
  /mode <name>          переключить режим ответа
  /system               показать текущий системный промпт
  /history              показать размер истории и примерную оценку токенов
  /reset                очистить историю диалога
  /save [path]          сохранить историю
  /load [path]          загрузить историю
  /config               показать текущие настройки клиента
  /exit                 выйти
""".strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='GigaVibeMiptCode console LLM assistant')
    parser.add_argument('--provider', choices=['mock', 'gigachat', 'openai'], help='LLM provider')
    parser.add_argument('--model', help='Model name')
    parser.add_argument('--max-context-tokens', type=int, help='Approximate context window budget')
    parser.add_argument('--history-file', type=Path, default=DEFAULT_HISTORY_FILE)
    parser.add_argument('--mode', default=None, help='Initial mode name')
    parser.add_argument('--once', help='Ask one question and exit')
    parser.add_argument('--no-save', action='store_true', help='Do not autosave history on exit')
    return parser


def _path_from_command(parts: list[str], default: Path) -> Path:
    if len(parts) >= 2:
        return Path(parts[1])
    return default


def handle_command(
    command: str,
    *,
    session: ChatSession,
    mode_name: str,
    config: AppConfig,
    history_file: Path,
) -> tuple[bool, str]:
    """Handle a slash command.

    Returns (should_continue_chat, current_mode_name).
    """

    try:
        parts = shlex.split(command)
    except ValueError as error:
        print(f'Не удалось разобрать команду: {error}')
        return True, mode_name

    if not parts:
        return True, mode_name

    name = parts[0]
    if name in {'/exit', '/quit'}:
        return False, mode_name
    if name == '/help':
        print(HELP_TEXT)
    elif name in {'/mode', '/modes'}:
        if len(parts) == 1:
            print(format_modes())
            print(f'Текущий режим: {mode_name}')
        else:
            new_mode = get_mode(parts[1])
            mode_name = new_mode.name
            print(f'Режим переключён: {new_mode.name} — {new_mode.title}')
    elif name == '/system':
        print(get_mode(mode_name).system_prompt)
    elif name == '/history':
        print(f'Сообщений в истории: {len(session.history)}')
        print(f'Примерная оценка токенов: {messages_tokens(session.history)}')
    elif name == '/reset':
        session.reset()
        print('История очищена.')
    elif name == '/save':
        path = _path_from_command(parts, history_file)
        save_history(path, mode_name, session.history)
        print(f'История сохранена: {path}')
    elif name == '/load':
        path = _path_from_command(parts, history_file)
        loaded_mode, loaded_history = load_history(path)
        mode_name = loaded_mode
        session.history[:] = loaded_history
        print(f'История загружена: {path}')
    elif name == '/config':
        print(f'provider: {config.provider}')
        print(f'model: {config.model}')
        print(f'max_context_tokens: {config.max_context_tokens}')
        print(f'temperature: {config.temperature}')
    else:
        print('Неизвестная команда. Напишите /help')

    return True, mode_name


def ask_once(question: str, session: ChatSession, mode_name: str, config: AppConfig) -> int:
    mode = get_mode(mode_name)
    client = create_client(config.provider)
    session.add_user_message(question)
    request_messages = session.build_request_messages(mode, config.max_context_tokens)
    try:
        answer = client.complete(request_messages, config)
    except LLMClientError as error:
        print(f'Ошибка LLM: {error}', file=sys.stderr)
        return 1
    session.add_assistant_message(answer)
    print(answer)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = AppConfig.from_env().with_overrides(
        provider=args.provider,
        model=args.model,
        max_context_tokens=args.max_context_tokens,
    )

    try:
        saved_mode, history = load_history(args.history_file)
    except Exception as error:
        print(f'Не удалось загрузить историю: {error}', file=sys.stderr)
        saved_mode, history = DEFAULT_MODE, []

    mode_name = args.mode or saved_mode
    get_mode(mode_name)  # validate early
    session = ChatSession(history=history)

    if args.once:
        code = ask_once(args.once, session, mode_name, config)
        if not args.no_save:
            save_history(args.history_file, mode_name, session.history)
        return code

    client = create_client(config.provider)
    print('GigaVibeMiptCode запущен. Напишите /help для справки, /exit для выхода.')
    print(f'Провайдер: {config.provider}, модель: {config.model}, режим: {mode_name}')

    should_continue = True
    while should_continue:
        try:
            user_input = input(f'\n[{mode_name}] Вы: ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.startswith('/'):
            should_continue, mode_name = handle_command(
                user_input,
                session=session,
                mode_name=mode_name,
                config=config,
                history_file=args.history_file,
            )
            continue

        mode = get_mode(mode_name)
        session.add_user_message(user_input)
        request_messages = session.build_request_messages(mode, config.max_context_tokens)

        try:
            answer = client.complete(request_messages, config)
        except LLMClientError as error:
            print(f'Ошибка LLM: {error}')
            continue

        session.add_assistant_message(answer)
        print(f'\nАссистент: {answer}')

    if not args.no_save:
        save_history(args.history_file, mode_name, session.history)
        print(f'История сохранена: {args.history_file}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
