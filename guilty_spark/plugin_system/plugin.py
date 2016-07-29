import asyncio
import discord
from guilty_spark.bot import Monitor


class Plugin:
    """ Base plugin class """

    def __init__(self, bot: Monitor, commands=None):
        """ Set's up the plugin's base resources

            Walks the Subclass's structure and search for any hooks
            to request

        :param bot:
            Monitor instance
        :param commands:
            A list of command strings to respond to if on_command is hooked
        """

        self.bot = bot
        self.depends = []

        self.commands = commands

        methods = [
            ('on_message', self.on_message),
            ('on_command', self.on_command)
        ]
        for dep, method in methods:
            if asyncio.iscoroutinefunction(method):
                self.depends.append(dep)

    def on_message(self, message: discord.Message):
        """ on_message discord.py hook """
        pass

    def on_command(self, command, message: discord.Message):
        """ on_command discord.py hook """
        pass

    @asyncio.coroutine
    def help(self):
        yield from self.bot.say("Help hasn't been added for this command yet")
