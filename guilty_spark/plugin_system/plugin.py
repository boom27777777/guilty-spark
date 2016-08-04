import asyncio
import discord
import yaml

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.data import plugin_file


class Plugin:
    """ Base plugin class """

    def __init__(self, name: str, bot: Monitor, commands=None):
        """ Set's up the plugin's base resources

            Walks the Subclass's structure and search for any hooks
            to request

        :param bot:
            Monitor instance
        :param commands:
            A list of command strings to respond to if on_command is hooked
        """

        self.name = name
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

        self.cache_file = self.name + '.cache'
        try:
            with plugin_file(self.cache_file) as cache:
                self.disabled_channels = yaml.load(cache)
        except IOError:
            self.disabled_channels = []

    def cache(self):
        with plugin_file(self.cache_file, 'w') as cache:
            yaml.dump(self.disabled_channels, cache)

    @property
    def enabled(self):
        if self.bot.current_message:
            chan_id = self.bot.current_message.channel.id
            if chan_id not in self.disabled_channels:
                return True
        return False

    def pre_message(self, message: discord.Message):
        if self.enabled:
            yield from self.on_message(message)

    def on_message(self, message: discord.Message):
        """ on_message discord.py hook """
        pass

    def pre_command(self, command, message: discord.Message):
        if self.enabled:
            yield from self.on_command(command, message)

    def on_command(self, command, message: discord.Message):
        """ on_command discord.py hook """
        pass

    def disable(self, channel_id):
        self.disabled_channels.append(channel_id)

    def enable(self, channel_id):
        self.disabled_channels.remove(channel_id)

    @asyncio.coroutine
    def help(self):
        yield from self.bot.say("Help hasn't been added for this command yet")

    def __repr__(self):
        return self.name
