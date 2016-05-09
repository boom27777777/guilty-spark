import asyncio
import logging

from os.path import curdir, join
from sys import argv

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
    if '--daemon' in argv or '-d' in argv:
        import daemon
        with daemon.DaemonContext(working_directory=curdir):
            main(join(curdir, 'bot.log'))
    else:
        main()
