import asyncio
import discord
from guilty_spark.bot import Monitor


class Plugin:
    def __init__(self, bot: Monitor):
        self.bot = bot
        self.depends = []

        try:
            getattr(self, 'commands')
        except AttributeError:
            self.commands = []

        methods = [
            ('on_message', self.on_message),
            ('on_command', self.on_command)
        ]
        for dep, method in methods:
            if asyncio.iscoroutinefunction(method):
                self.depends.append(dep)


    def on_message(self, message: discord.Message):
        pass

    def on_command(self, message: discord.Message):
        pass

    @asyncio.coroutine
    def help(self):
        yield from self.bot.say("Help hasn't been added for this command yet")
