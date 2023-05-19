import asyncio
import logging
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import Config, load_config
from handlers import other_handlers, Handlers

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filenam'
               'e)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()

    subprocess.run(f"python3 services/clear_directory.py users_files", shell=True)
    subprocess.run(f"mkdir users_files", shell=True)
    subprocess.run(f"python3 services/clear_directory.py telegram-bot-api/bin/{config.tg_bot.token}/documents",
                   shell=True)
    subprocess.run(f"python3 services/clear_directory.py telegram-bot-api/bin/{config.tg_bot.token}/photos", shell=True)

    session = AiohttpSession(api=TelegramAPIServer.from_base('http://127.0.0.1:8081/'))

    bot: Bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML', session=session)

    storage: MemoryStorage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(Handlers.router)
    # dp.include_router(user_handlers.router)
    # dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
