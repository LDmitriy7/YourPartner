"""Main script, starts bot in long-polling mode."""

from aiogram import executor, Dispatcher

from loader import dp


async def on_startup(*_):
    import logging
    import handlers
    import filters

    logging.basicConfig(level=20)
    logger = logging.getLogger(__name__)
    logger.info('Import %s', handlers)
    logger.info('Import %s', filters)


async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
