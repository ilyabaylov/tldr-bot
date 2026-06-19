# tldr-bot

Telegram-бот для коротких выжимок из текста, ссылок, YouTube, PDF и голосовых.

Пользователь отправляет материал и получает понятный ответ. Под ответом есть кнопки: сменить формат или задать вопрос по тому же источнику.

## Возможности

- Текст и пересланные сообщения
- Статьи по ссылке
- YouTube по субтитрам
- PDF, TXT и MD файлы
- Голосовые и аудио
- Форматы ответа: TL;DR, тезисы, идеи, действия, простое объяснение
- Вопросы по последнему источнику
- Русский и английский язык ответа
- OpenAI, Gemini или OpenAI-совместимый API: OpenRouter, NVIDIA, Groq

<img src="https://github.com/ilyabaylov/tldr-bot/blob/main/demo.gif?raw=true">

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/setup_env.py
python scripts/check_config.py
python -m app.bot
```

На Windows:

```powershell
.venv\Scripts\python scripts\setup_env.py
.venv\Scripts\python scripts\check_config.py
.venv\Scripts\python -m app.bot
```

`setup_env.py` создаёт `.env` и спрашивает всё нужное: токен бота, провайдера, ключ, модель, голосовые.

Если `.env` уже есть, скрипт сделает резервную копию.

## Ручная настройка OpenAI

```env
BOT_TOKEN=твой_telegram_bot_token

LLM_PROVIDER=openai
CHAT_MODEL=gpt-5-mini
LLM_API_KEY=твой_openai_key
LLM_BASE_URL=

GEMINI_API_KEY=

TRANSCRIBE_PROVIDER=openai
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
TRANSCRIBE_API_KEY=
TRANSCRIBE_BASE_URL=

DB_PATH=data/tldr.db
RATE_LIMIT_PER_MIN=10
MAX_INPUT_CHARS=20000
```

`LLM_BASE_URL` для обычного OpenAI оставь пустым.

`TRANSCRIBE_API_KEY` тоже можно оставить пустым. Тогда для голосовых будет использоваться `LLM_API_KEY`.

Если голосовые не нужны:

```env
TRANSCRIBE_PROVIDER=none
```

После правки `.env` всегда перезапускай бота.

## Проверка настроек

```bash
python scripts/check_config.py
```

Скрипт покажет:

- какой провайдер выбран;
- какая модель используется;
- включены ли голосовые;
- какие переменные заполнены неправильно.

## Частая ошибка с голосовыми

Если в логах видно Google/Gemini:

```text
google_genai.models
API key not valid
```

значит голосовые идут в Gemini. Для OpenAI-ключа нужно:

```env
TRANSCRIBE_PROVIDER=openai
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
```

Подробно: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

## Команды

| Команда | Что делает |
| --- | --- |
| `/start` | краткое описание |
| `/settings` | язык и длина ответа |
| `/help` | помощь |

## Структура

```text
app/
├─ bot.py              # запуск бота
├─ config.py           # настройки из .env
├─ config_validation.py # проверка настроек
├─ db.py               # SQLite
├─ handlers/           # команды, контент, кнопки
├─ llm/                # OpenAI / Gemini / совместимые API
├─ services/           # основная логика
└─ utils/              # небольшие утилиты
scripts/
├─ setup_env.py        # создание .env
└─ check_config.py     # проверка .env
```

Документация:

- [`docs/SETUP.md`](docs/SETUP.md)
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Тесты

```bash
pip install pytest
pytest -q
```

Часть логики проверяется без сети и ключей: промпты, ссылки, YouTube ID, лимит Telegram, память контекста, рейт-лимит и валидация `.env`.

## Docker

```bash
docker build -t tldr-bot .
docker run --env-file .env -v $(pwd)/data:/app/data tldr-bot
```

## Лицензия

MIT
