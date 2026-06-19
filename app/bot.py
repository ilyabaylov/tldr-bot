"""Запуск бота."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.config_validation import format_report, validate_or_raise, validate_settings
from app.db import init_db
from app.handlers import actions, commands, content
from app.logging_setup import setup_logging, startup_banner

log = logging.getLogger("tldr")


async def main() -> None:
    setup_logging()

    report = validate_settings(settings)
    for warning in report.warnings:
        log.warning(warning)
    validate_or_raise(settings)

    print(startup_banner(settings), flush=True)

    await init_db()
    log.info("Database ready: %s", settings.db_path)

    bot = Bot(
        settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=MemoryStorage())
    # Порядок важен: actions раньше content, чтобы перехватить вопрос в состоянии Ask.
    dp.include_router(commands.router)
    dp.include_router(actions.router)
    dp.include_router(content.router)

    me = await bot.get_me()
    log.info("Connected as @%s", me.username)
    log.info("Polling started. Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def run() -> None:
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger("tldr").info("Stopped.")


if __name__ == "__main__":
    run()
