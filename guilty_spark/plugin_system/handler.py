"""
:Date: 2016-08-04
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import discord
import yaml

from guilty_spark.plugin_system.data import plugin_file


class Handler:
    def __init__(self, plugin):
        self.plugin = plugin
        self.cache_file = plugin.name + '.cache'

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
        if self.plugin.bot.current_message:
            chan_id = self.plugin.bot.current_message.channel.id
            if chan_id not in self.disabled_channels:
                return True
        return False

    def on_command(self, command: str, message: discord.Message):
        if self.enabled:
            yield from self.plugin.on_command(command, message)

    def on_message(self, message: discord.Message):
        if self.enabled:
            yield from self.plugin.on_message(message)

    def disable(self, channel_id):
        self.disabled_channels.append(channel_id)

    def enable(self, channel_id):
        self.disabled_channels.remove(channel_id)
