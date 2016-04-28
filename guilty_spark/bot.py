import discord
import yaml
import asyncio
import logging
import os


class Monitor(discord.Client):
    def __init__(self, settings_file: str = '', **options):
        super().__init__(**options)
        self.event_callbacks = {}
        self.description = 'I am the Monitor of Installation 04. ' \
                           'I am 343 Guilty Spark'

        if not os.path.exists(settings_file):
            print('No settings file found, making one for you now.')
            with open(settings_file, 'w') as settings:
                yaml.dump({'owner': '', 'token': ''}, settings,
                          default_flow_style=False)
            raise IOError

        with open(settings_file) as settings:
            self.settings = yaml.load(settings)

        self.current_message = None

    def login(self, *args):
        yield from super().login(self.settings['token'])

    def register_function(self, name: str, func):
        if name not in self.event_callbacks:
            self.event_callbacks[name] = []
        self.event_callbacks[name].append(func)

    def say(self, message: str):
        if self.current_message:
            yield from self.send_message(self.current_message.channel, message)

    @asyncio.coroutine
    def on_ready(self):
        logging.info('Connected as %s(%s)', self.user.name, self.user.id)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        logging.info(
            '%s:%s: %s',
            message.channel,
            message.author.name,
            message.content
        )
        if message.author == self.user:
            return

        self.current_message = message

        if message.content == '!help':
            yield from self.say(
                self.description +
                '\nTry !help [command] if you need specific help any command')
            return

        for func in self.event_callbacks['on_message']:
            yield from func(message)
