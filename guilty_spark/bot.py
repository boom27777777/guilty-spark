import discord
import yaml
import asyncio
import logging
import os


class Monitor(discord.Client):
    def __init__(self, settings_file: str = '', **options):
        super().__init__(**options)
        self.callbacks = {}
        self.commands = {}
        self.description = 'I am the Monitor of Installation 04. ' \
                           'I am 343 Guilty Spark'

        if not os.path.exists(settings_file):
            print('No settings file found, making one for you now.')
            with open(settings_file, 'w') as settings:
                yaml.dump({'owner': '', 'token': '', 'command_prefix': '!'},
                          settings, default_flow_style=False)
            raise IOError

        with open(settings_file) as settings:
            self.settings = yaml.load(settings)

        self.prefix = self.settings['command_prefix']
        self.current_message = None

    def login(self, *args):
        yield from super().login(self.settings['token'])

    def register_plugin(self, name: str, obj):
        for dep in obj.depends:
            if dep not in self.callbacks:
                self.callbacks[dep] = []
            self.callbacks[dep].append(obj)

        for command in obj.commands:
            self.commands[self.prefix + command] = obj

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

        if message.content.startswith(self.prefix):
            if '!help' in message.content:
                args = message.content.split()
                if len(args) == 1 or len(args) > 2:
                    yield from self.say(
                        self.description +
                        '\nTry !help [command] if you need specific help any command')
                else:
                    command = args[1]
                    if not command.startswith(self.prefix):
                        command = self.prefix + command

                    if command in self.commands:
                        yield from self.commands[command].help()

                    else:
                        yield from self.say("I'm not familiar with that "
                                            "command, curious")

                return

            for command, plugin in self.commands.items():
                if command in message.content:
                    yield from plugin.on_command(message)

        for plugin in self.callbacks.setdefault('on_message', []):
            yield from plugin.on_message(message)
