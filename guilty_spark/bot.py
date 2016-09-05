import asyncio

import datetime
import discord
import logging

import guilty_spark.config as config
from guilty_spark.util import slice_message, cap_message
from guilty_spark.plugin_system.manager import PluginManager


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

        self.plugin_manager = PluginManager()
        self.plugin_manager.load()

        self.settings = config.load_config(settings_file)

        self.prefix = self.settings['command_prefix']
        self.current_message = None

    def login(self, *args):
        """ Send the initial login payload"""
        yield from self.load_plugins()
        yield from super().login(self.settings['token'])

    @asyncio.coroutine
    def load_plugins(self):
        if not self.plugin_manager:
            return

        for plug in self.plugin_manager.make_plugs(self):
            yield from self._register_plugin(plug)

    @asyncio.coroutine
    def _register_plugin(self, obj):
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

        yield from obj.on_load()

    def send_message(self, destination, content, *args, tts=False, **kwargs):
        """ Sends message through the discord api

            This method will split up messages longer then the character_max
            setting in the config

        :param kwargs:
            :key: "ends" what to wrap each message in
        """

        limit = self.settings['character_limit']
        ends = kwargs.setdefault('ends', '')
        if len(content) > limit:
            parts = slice_message(
                limit, content, ends)

            for part in parts:
                yield from super().send_message(
                    destination, part, *args, tts=tts)

        else:
            if isinstance(ends, list):
                content = cap_message(content, ends[0], ends[1])
            else:
                content = cap_message(content, ends, ends)
            yield from super().send_message(
                destination, content, *args, tts=tts)

    def say(self, message: str, ends=None):
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

    def code(self, message: str, language=''):
        """ Wrap a **bot.say()** message in a code block

        :param message:
            The code to send
        :param language:
            The language of the given code
        """

        ends = ['```' + language + '\n', '```']
        yield from self.say(message, ends=ends)

    @asyncio.coroutine
    def on_ready(self):
        """ |coro|

            Adds a line to the log with the bot's username and id
            on a successful connection
        """

        logging.info('Connected as %s(%s)', self.user.name, self.user.id)

    def call_hooks(self, dep: str, *args, **kwargs):
        """

            Iterates through the attached plugins and calls any plugin
            with the relevant hooks

        :param dep:
            The dependency to test for
        """
        for plugin in self.callbacks.setdefault(dep, []):
            if plugin.enabled:
                yield from getattr(plugin, dep)(*args, **kwargs)

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
                    yield from plugin.on_command(args[0], message)
            return

        # Run all on_message hooks
        yield from self.call_hooks('on_message', message)

    @asyncio.coroutine
    def on_message_delete(self, message: discord.Message):
        """ on_message_delete discord.py hook """
        yield from self.call_hooks('on_message_delete', message)

    @asyncio.coroutine
    def on_message_edit(self, before: discord.Message, after: discord.Message):
        """ on_message_edit discord.py hook """
        yield from self.call_hooks('on_message_edit', before, after)

    @asyncio.coroutine
    def on_channel_delete(self, channel: discord.Channel):
        """ on_channel_delete discord.py hook """
        yield from self.call_hooks('on_channel_delete', channel)

    @asyncio.coroutine
    def on_channel_create(self, channel: discord.Channel):
        """ on_channel_create discord.py hook """
        yield from self.call_hooks('on_channel_create', channel)

    @asyncio.coroutine
    def on_channel_update(self, before: discord.Channel,
                          after: discord.Channel):
        """ on_channel_update discord.py hook """
        yield from self.call_hooks('on_channel_update', before, after)

    def on_member_join(self, member: discord.Member):
        """ on_member_join discord.py hook """
        yield from self.call_hooks('on_member_join', member)

    @asyncio.coroutine
    def on_member_remove(self, member: discord.Member):
        """ on_member_remove discord.py hook """
        yield from self.call_hooks('on_member_remove', member)

    @asyncio.coroutine
    def on_member_update(self, before: discord.Member, after: discord.Member):
        """ on_member_update discord.py hook """
        yield from self.call_hooks('on_member_update', before, after)

    @asyncio.coroutine
    def on_server_join(self, server: discord.Server):
        """ on_server_join discord.py hook """
        yield from self.call_hooks('on_server_join', server)

    @asyncio.coroutine
    def on_server_remove(self, server: discord.Server):
        """ on_server_remove discord.py hook """
        yield from self.call_hooks('on_server_remove', server)

    @asyncio.coroutine
    def on_server_update(self, before: discord.Server, after: discord.Server):
        """ on_server_update discord.py hook """
        yield from self.call_hooks('on_server_update', before, after)

    @asyncio.coroutine
    def on_server_role_create(self, role: discord.Role):
        """ on_server_role_create discord.py hook """
        yield from self.call_hooks('on_server_role_create', role)

    @asyncio.coroutine
    def on_server_role_updated(self, before: discord.Role,
                               after: discord.Role):
        """ on_server_role_updated discord.py hook """
        pass

    @asyncio.coroutine
    def on_server_emojis_update(self, before: discord.Server,
                                after: discord.Server):
        """ on_server_em discord.py hook """
        yield from self.call_hooks('on_server_emojis_update', before, after)

    @asyncio.coroutine
    def on_server_available(self, server: discord.Server):
        """ on_server_available discord.py hook """
        yield from self.call_hooks('on_server_available', server)

    @asyncio.coroutine
    def on_server_unavailable(self, server: discord.Server):
        """ on_server_unavailable discord.py hook """
        yield from self.call_hooks('on_server_unavailable', server)

    @asyncio.coroutine
    def on_voice_state_update(self, before: discord.Member,
                              after: discord.Member):
        """ on_voice_state_update discord.py hook """
        yield from self.call_hooks('on_voice_state_update', before, after)

    @asyncio.coroutine
    def on_member_ban(self, member: discord.Member):
        """ on_member_ban discord.py hook """
        yield from self.call_hooks('on_member_ban', member)

    @asyncio.coroutine
    def on_member_unban(self, server: discord.Server, user: discord.User):
        """ on_member_unban discord.py hook """
        yield from self.call_hooks('on_member_unban', server, user)

    @asyncio.coroutine
    def on_typing(self, channel: discord.Channel, user: discord.User,
                  when: datetime.datetime):
        """ on_typing discord.py hook """
        yield from self.call_hooks('on_typing', channel, user, when)

    @asyncio.coroutine
    def on_group_join(self, channel: discord.Channel, user: discord.User):
        """ on_group_join discord.py hook """
        yield from self.call_hooks('on_group_join', channel, user)

    @asyncio.coroutine
    def on_group_remove(self, channel: discord.Channel, user: discord.User):
        """ on_group_remove discord.py hook """
        yield from self.call_hooks('on_group_remove', channel, user)
