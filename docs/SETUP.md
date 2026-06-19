# Настройка .env

Самый простой способ — запустить мастер настройки:

```bash
python scripts/setup_env.py
```

На Windows:

```powershell
.venv\Scripts\python scripts\setup_env.py
```

Скрипт спросит:

- токен Telegram-бота;
- провайдера модели;
- ключ OpenAI / Gemini / OpenRouter;
- модель для выжимок;
- включать ли голосовые;
- модель для расшифровки голосовых.

Если `.env` уже есть, скрипт сделает резервную копию вида:

```text
.env.backup-20260619-162900
```

## Быстрый конфиг для OpenAI

Если настраиваешь вручную, для OpenAI поставь так:

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

`TRANSCRIBE_API_KEY` можно оставить пустым. Тогда бот возьмёт `LLM_API_KEY`.

`LLM_BASE_URL` для обычного OpenAI тоже оставь пустым.

## Почему голосовое могло не работать

Если в `.env` стоит:

```env
LLM_PROVIDER=openai
TRANSCRIBE_PROVIDER=gemini
```

то текстовые запросы идут в OpenAI, а голосовые — в Gemini. Если Gemini-ключ не указан или неверный, голосовые падают с ошибкой Google API.

Для OpenAI-ключа нужно так:

```env
TRANSCRIBE_PROVIDER=openai
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
```

И после изменения `.env` нужно перезапустить бота.
