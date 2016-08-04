"""
:Date: 2016-08-04
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import asyncio
import discord

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.plugin_system.data import plugin_file


class RP(Plugin):
    def __init__(self, name: str, bot: Monitor):
        super().__init__(name, bot, commands=['rp'])
        self.usage = self.bot.prefix + 'rp [record|report]'
        self.sessions = {}

    def start_session(self, channel_id: str):
        self.sessions[channel_id] = plugin_file(channel_id + '.txt', 'a')

    def stop_session(self, channel_id: str):
        self.sessions[channel_id].close()

    def upload_log(self, channel: discord.Channel):
        with plugin_file(channel.id + '.txt') as log:
            yield from self.bot.send_file(channel, log)

    @asyncio.coroutine
    def help(self):
        yield from self.bot.code(
            'A simple helper for Role playing\n'
            '    record - Start recording a log for a session\n'
            '    stop   - Stop recording a session\n'
            '    upload - Upload the recorded log\n'
            + self.usage
        )

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        args = message.content.split()
        if len(args) < 2:
            yield from self.bot.say(self.usage)

        _, sub_command, *args = args

        if sub_command == 'record':
            self.start_session(message.channel.id)
            yield from self.bot.say('Recording started')

        elif sub_command == 'stop':
            try:
                self.start_session(message.channel.id)
                yield from self.bot.say('Recording stopped')
            except KeyError:
                yield from self.bot.say('No recording active')

        elif sub_command == 'upload':
            yield from self.upload_log(message.channel)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        if message.channel.id in self.sessions:
            self.sessions[message.channel.id].write(
                '{}:    {}\n'.format(
                    message.author.display_name,
                    message.content
                ))
