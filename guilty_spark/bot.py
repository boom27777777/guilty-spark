import asyncio
import discord
import logging

import guilty_spark.config as config
from guilty_spark.util import slice_message, cap_message


class Monitor(discord.Client):
    """The main subclass of the Discord client"""

    def __init__(self, settings_file: str = '', **options):
        """ Sets up our bot

        :param settings_file:
            The location to search for a settings file
        :param options:
            Optional settings to be passed along to the base class constructor

        :raises IOError:
            If settings file is not found
        """

        super().__init__(**options)

        self.callbacks = {}
        self.commands = {}
        self.plugins = {}
        self.description = 'I am the Monitor of Installation 04. ' \
                           'I am 343 Guilty Spark'

        self.help_message = self.description + \
            '\nTry !help [command] if you need specific help any command'

        #
        self.settings = config.load_config(settings_file)

        self.prefix = self.settings['command_prefix']
        self.current_message = None

    def login(self, *args):
        """ Send the initial login payload"""

        yield from super().login(self.settings['token'])

    def register_plugin(self, obj):
        """ Bind a new plugin to the bot

            Also walks the plugin dependinces to avoid having to iterate
            through the entire discord api on every event.

        :param obj:
            The new **guilty_spark.plugin_system.plugin.Plugin** Subclass to
            bind
        """
        for dep in obj.depends:
            if dep not in self.callbacks:
                self.callbacks[dep] = []
            self.callbacks[dep].append(obj)

        if obj.commands:
            for command in obj.commands:
                # TODO Add some kind of command collision handling
                self.commands[self.prefix + command] = obj

        self.plugins[obj.name] = obj

    def send_message(self, destination, content, *args, tts=False, **kwargs):
        """ Sends message through the discord api

            This method will split up messages longer then the character_max
            setting in the config

        :param kwargs:
            :key: "ends" what to wrap each message in
        """

        limit = self.settings['character_limit']
        if len(content) > limit:
            parts = slice_message(
                limit, content, kwargs.setdefault('ends', ''))

            for part in parts:
                yield from super().send_message(
                    destination, part, *args, tts=tts)

        else:
            content = cap_message(content, kwargs.setdefault('ends', ''))
            yield from super().send_message(
                destination, content, *args, tts=tts)

    def say(self, message: str, ends=''):
        """ Return a context dependant message

            Checks the bot's current message property and sends a message back
            to the originating channel

        :param ends:
            String to wrap a message in (IE * -> *text*)
        :param message:
            The text to send
        """

        if self.current_message:
            yield from self.send_message(
                self.current_message.channel, message, ends=ends)

    def code(self, message: str):
        """ Wrap a **bot.say()** message in a code block

        :param message:
            The code to send
        """

        yield from self.say('\n' + message, ends='```')

    @asyncio.coroutine
    def on_ready(self):
        """ |coro|

            Adds a line to the log with the bot's username and id
            on a successful connection
        """

        logging.info('Connected as %s(%s)', self.user.name, self.user.id)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        """ |coro|

            Overload of base Client's on_message event. Parses any incoming
            message for commands, and runs plugin's on_message hook
            accordingly.

        :param message:
            discord.Message Message object handed to us by discord.py
        """

        # Log the incoming message
        logging.info(
            '%s:%s: %s',
            message.channel,
            message.author.name,
            message.content
        )
        # Ignore all messages coming from our own client to prevent loops
        if message.author == self.user:
            return

        # Set the contextual message property
        self.current_message = message

        # Parse the message for our command character
        if message.content.startswith(self.prefix):

            # Test our available commands for a matching signature and pass
            # the message onto the appropriate plugin on_command hook
            args = message.content.split()
            for command, plugin in self.commands.items():
                if command == args[0]:
                    yield from plugin.pre_command(args[0], message)
            return

        # Run all on_message hooks
        for plugin in self.callbacks.setdefault('on_message', []):
            yield from plugin.pre_message(message)
