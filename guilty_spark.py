import asyncio

from guilty_spark.application import bot


def main():
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
