import asyncio
import logging

from guilty_spark.application import bot
from guilty_spark.plugin_system.manager import PluginManager


def main(log=None):
    if log:
        log = open(log, 'a')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s|%(levelname)s|%(message)s',
        filename=log
    )

    # Setup and Bind plugin manager to our bot instance
    plugin_manager = PluginManager()
    plugin_manager.load()
    plugin_manager.bind(bot)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.login())
        loop.run_until_complete(bot.connect())
    except Exception:
        loop.run_until_complete(bot.logout())
        loop.run_until_complete(bot.close())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
