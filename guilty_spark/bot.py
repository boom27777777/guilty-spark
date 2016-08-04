import asyncio
import discord
import logging

from guilty_spark import config


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

    def register_plugin(self, name: str, obj):
        """ Bind a new plugin to the bot

            Also walks the plugin dependinces to avoid having to iterate
            through the entire discord api on every event.

        :param name:
            Plugin name (Deprecated)
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

    def say(self, message: str):
        """ Return a context dependant message

            Checks the bot's current message property and sends a message back
            to the originating channel

        :param message:
            The text to send
        """

        if self.current_message:
            yield from self.send_message(self.current_message.channel, message)

    def code(self, message: str):
        """ Wrap a **bot.say()** message in a code block

        :param message:
            The code to send
        """
        yield from self.say('```{}```'.format(message))

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

            # Special logic for a !help command
            if '!help' in message.content:
                args = message.content.split()
                if len(args) == 1 or len(args) > 2:
                    commands = '\n\nThe commands I know are:\n\t'
                    commands += '\n\t'.join([c for c in self.commands])
                    yield from self.code(self.help_message + commands)
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

            # Test our available commands for a matching signature and pass
            # the message onto the appropriate plugin on_command hook
            args = message.content.split()
            for command, plugin in self.commands.items():
                if command == args[0]:
                    yield from plugin.on_command(args[0], message)
            return

        # Run all on_message hooks
        for plugin in self.callbacks.setdefault('on_message', []):
            yield from plugin.on_message(message)
