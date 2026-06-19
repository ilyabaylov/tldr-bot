# Troubleshooting

## Голосовые идут в Gemini, хотя ключ OpenAI

Симптом в логах:

```text
google_genai.models
API key not valid
```

Причина: в `.env` стоит:

```env
TRANSCRIBE_PROVIDER=gemini
```

Для OpenAI-ключа поставь:

```env
TRANSCRIBE_PROVIDER=openai
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
TRANSCRIBE_API_KEY=
TRANSCRIBE_BASE_URL=
```

`TRANSCRIBE_API_KEY` можно оставить пустым — будет использован `LLM_API_KEY`.

После изменения `.env` перезапусти бота.

## Текст работает, голосовые нет

Проверь:

```env
LLM_PROVIDER=openai
LLM_API_KEY=...
TRANSCRIBE_PROVIDER=openai
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
```

Потом запусти:

```bash
python scripts/check_config.py
```

На Windows:

```powershell
.venv\Scripts\python scripts\check_config.py
```

## Бот падает при старте

Сначала проверь конфиг:

```bash
python scripts/check_config.py
```

Частые причины:

- пустой `BOT_TOKEN`;
- пустой `LLM_API_KEY` при `LLM_PROVIDER=openai`;
- `TRANSCRIBE_PROVIDER=gemini`, но `GEMINI_API_KEY` пустой;
- опечатка в названии провайдера.

## OpenAI возвращает ошибку ключа

Проверь, что ключ вставлен без пробелов и кавычек:

```env
LLM_API_KEY=sk-...
```

Не так:

```env
LLM_API_KEY="sk-..."
```

## YouTube не обработался

Бот берёт субтитры. Если у ролика нет доступных субтитров, он покажет ошибку.

Для проверки лучше брать ролики, где в YouTube реально включаются subtitles / captions.

## PDF не обработался

Поддерживаются PDF, TXT и MD.

Если PDF — скан без текста, бот может не прочитать его. OCR в проект пока не добавлен.

## После правки .env ничего не изменилось

`.env` читается при запуске. Нужно перезапустить бота:

```powershell
Ctrl+C
.venv\Scripts\python -m app.bot
```
