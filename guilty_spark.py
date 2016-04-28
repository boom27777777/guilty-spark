import logging
import asyncio

from guilty_spark.application import bot
from guilty_spark.plugin import PluginManager


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s|%(levelname)s|%(message)s',
        filename=None
    )

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
