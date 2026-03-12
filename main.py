import asyncio
import logging
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from middlewares.auth import AdminMiddleware
from handlers import mtproxy

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    level=config.LOG_LEVEL,
)
logger = logging.getLogger(__name__)


async def main():
    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env")
    if not config.ADMIN_IDS:
        raise ValueError("ADMIN_IDS не задан в .env")

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(AdminMiddleware())
    dp.include_router(mtproxy.router)

    retry_count = 0
    while True:
        try:
            logger.info("Бот запускается...")
            retry_count = 0
            await dp.start_polling(bot, skip_updates=True)
        except KeyboardInterrupt:
            logger.info("Остановлен.")
            break
        except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionError) as e:
            retry_count += 1
            delay = min(5 * (2 ** (retry_count - 1)), 300)
            logger.warning("Ошибка сети (%d): %s — повтор через %ds", retry_count, e, delay)
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error("Критическая ошибка: %s", e, exc_info=True)
            await asyncio.sleep(10)
        finally:
            try:
                await bot.session.close()
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
