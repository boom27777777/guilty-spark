import asyncio
import logging

from guilty_spark.application import bot, logger


def main(log=None):
    if log:
        log = open(log, 'a')

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.login())
        loop.run_until_complete(bot.connect())
    except Exception:
        loop.run_until_complete(bot.logout())
        loop.run_until_complete(bot.close())
        raise
    finally:
        loop.close()


if __name__ == '__main__':
    main()
