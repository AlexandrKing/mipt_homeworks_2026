# Итоговый проект "GigaVibeMiptCode"

Консольный ИИ-ассистент на Python: принимает сообщения пользователя, хранит историю диалога, добавляет системный промпт выбранного режима, обрезает старые сообщения при переполнении контекстного окна и отправляет запрос в LLM.

## Возможности

- консольный чат;
- системный промпт;
- история сообщений с ролями `user` и `assistant`;
- примерное ограничение контекстного окна и удаление старых сообщений;
- режимы ответов: `assistant`, `code`, `teacher`, `concise`, `creative`;
- сохранение и загрузка истории;
- три провайдера:
  - `mock` — offline-режим без внешней модели;
  - `gigachat` — через официальный пакет `gigachat`;
  - `openai` — любой OpenAI-compatible `/chat/completions` endpoint.

## Быстрый запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python run.py
```

По умолчанию включён `mock`-режим. Он нужен, чтобы приложение запускалось без API-ключей.

## Запуск с GigaChat

```bash
pip install -e ".[gigachat]"
export LLM_PROVIDER=gigachat
export GIGACHAT_CREDENTIALS="ваш_ключ_авторизации"
export LLM_MODEL="GigaChat"
python run.py
```

Если на локальной машине не настроены TLS-сертификаты, для учебного запуска можно временно использовать:

```bash
export GIGACHAT_VERIFY_SSL_CERTS=false
```

Для production-сценариев лучше настроить сертификаты и оставить проверку включённой.

## Запуск с OpenAI-compatible API

```bash
export LLM_PROVIDER=openai
export LLM_API_KEY="ваш_api_key"
export LLM_API_URL="https://api.openai.com/v1/chat/completions"
export LLM_MODEL="gpt-4o-mini"
python run.py
```

## Команды внутри чата

```text
/help                 показать справку
/mode                 показать режимы
/mode code            переключиться в режим программирования
/system               показать текущий системный промпт
/history              показать размер истории и примерную оценку токенов
/reset                очистить историю
/save [path]          сохранить историю
/load [path]          загрузить историю
/config               показать настройки
/exit                 выйти
```

## Одноразовый запрос

```bash
python run.py --provider mock --once "Привет!"
```

## Проверки

```bash
python -m unittest discover -s tests -v
ruff check .
```

`ruff check` требует установленного `ruff`:

```bash
pip install ruff
```

## Структура проекта

```text
gigavibe_mipt_code/
├── gigavibe/
│   ├── cli.py          # консольный интерфейс и команды
│   ├── config.py       # настройки из переменных окружения
│   ├── context.py      # оценка токенов и обрезка истории
│   ├── llm_client.py   # клиенты mock/gigachat/openai-compatible
│   ├── messages.py     # модель сообщения
│   ├── modes.py        # режимы и системные промпты
│   ├── session.py      # состояние чата
│   └── storage.py      # сохранение/загрузка истории
├── tests/
├── run.py
├── pyproject.toml
├── requirements.txt
└── ruff.toml
```
