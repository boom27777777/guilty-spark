import asyncio
import datetime
import discord
import logging
import traceback

import guilty_spark.config as config
from guilty_spark.util import slice_message, cap_message
from guilty_spark.plugin_system.manager import PluginManager
from guilty_spark.plugin_system.plugin import Plugin


class Monitor(discord.Client):
    """The main subclass of the Discord client"""

    def __init__(self, settings_file, **options):
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
        self.sounds = {}
        self.volume = 1.0

    async def login(self, *args):
        """ Send the initial login payload"""
        await self.load_plugins()
        await super().login(self.settings['token'])

    async def load_plugins(self):
        if not self.plugin_manager:
            return

        for plug in self.plugin_manager.make_plugs(self):
            try:
                await self._register_plugin(plug)
            except BaseException as e:
                logging.error("Failed to register plugin: " + plug.name)

    async def _register_plugin(self, obj):
        """ Bind a new plugin to the bot

            Also walks the plugin dependencies to avoid having to iterate
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

        await obj.on_load()

    async def send_message(self, destination, content, *args, tts=False, **kwargs):
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
                await destination.send(
                    part, *args, tts=tts)

        else:
            if isinstance(ends, list):
                content = cap_message(content, ends[0], ends[1])
            else:
                content = cap_message(content, ends, ends)
            await destination.send(
                content, *args, tts=tts)

    async def say(self, message, ends=None):
        """ Return a context dependant message

            Checks the bot's current message property and sends a message back
            to the originating channel

        :param ends:
            String to wrap a message in (IE * -> *text*)
        :param message:
            The text to send
        """

        if self.current_message:
            await self.send_message(
                self.current_message.channel, message, ends=ends)

    async def send_embed(self, embed, channel=None):
        if type(channel) is str:
            for chan in self.get_all_channels():
                if chan.id == channel:
                    channel = chan
        if channel:
            await self.current_message.channel.send(channel, embed=embed)
        else:
            await self.current_message.channel.send(self.current_message.channel, embed=embed)

    async def send_file(self, destination, file, filename):
        await destination.send(file=discord.File(file, filename=filename))

    async def code(self, message, language=''):
        """ Wrap a **bot.say()** message in a code block

        :param message:
            The code to send
        :param language:
            The language of the given code
        """

        ends = ['```' + language + '\n', '```']
        await self.say(message, ends=ends)

    async def play_sound(self, file_path):
        """ Play a sound file with ffmpeg in the user's voice channel

        :param file_path:
            The file path to play
        :param target:
            The user who's channel you want to join
        """

        voice_chan = self.current_message.author.voice.voice_channel
        try:
            voice = await self.join_voice_channel(voice_chan)
        except discord.errors.ClientException:
            logging.warning('Sound already playing in channel {}'.format(
                voice_chan.name))
            return

        if not voice:
            return

        player = voice.create_ffmpeg_player(
            file_path,
            options='-filter:a loudnorm'
        )
        self.sounds[voice_chan.id] = player
        player.volume = self.volume
        player.start()

        while player.is_playing():
            await asyncio.sleep(0.1)

        await voice.disconnect()
        del self.sounds[voice_chan.id]

    async def stop_sound(self):
        """ Stops the currently playing sound in the user's channel

        :param target:
            The user who's channel you want to stop sounds in
        """

        voice_chan = self.current_message.author.voice.voice_channel
        if voice_chan.id in self.sounds:
            self.sounds[voice_chan.id].stop()

    def get_volume(self):
        voice_chan = self.current_message.author.voice.voice_channel
        if voice_chan.id in self.sounds:
            return self.sounds[voice_chan.id].volume
        else:
            return 0.0

    def set_volume(self, volume):
        voice_chan = self.current_message.author.voice.voice_channel
        self.volume = volume
        if voice_chan.id in self.sounds:
            self.sounds[voice_chan.id].volume = volume

    def get_user_by_id(self, user_id):
        for member in self.get_all_members():
            if member.id == user_id:
                return member

    async def log_plugin_error(self, plugin, error, hook, *args):
        # Decode arguments
        arg_str = []
        for arg in args:
            if hasattr(arg, 'content'):
                arg_str.append('<Message: "{}">'.format(arg.content))
            else:
                arg_str.append(str(arg))

        report = 'Error in plugin {}.{}({}):\n {}'.format(
            str(plugin),
            str(hook),
            ', '.join(arg_str),
            str(error) + '\n```\n' + traceback.format_exc() + '\n```'
        )

        logging.error(report)

        owner = self.get_user_by_id(self.settings['owner'])

        await self.send_message(owner, report)

    async def parse_command(self, message):
        """ |coro|

            Test our available commands for a matching signature and pass the
            message onto the appropriate plugin on_command hook
            :param message:
                Discord message object to parse
        """

        command, *_ = message.content.split()
        try:
            plugin = self.commands[command]
        except KeyError:
            return

        if not plugin.enabled:
            return

        if not Plugin.has_permissions(message.author, plugin.on_command):
            await self.send_embed(Plugin.build_embed(
                title="Error",
                description="You don't have permission to access that system",
                level=2
            ))
            return

        try:
            await plugin.on_command(command, message)
        except BaseException as e:
            await self.log_plugin_error(
                plugin,
                e,
                'on_command',
                command,
                message
            )

        return

    async def call_hooks(self, dep, *args, **kwargs):
        """ |coro|

            Iterates through the attached plugins and calls any plugin
            with the relevant hooks

        :param dep:
            The dependency to test for
        """
        for plugin in self.callbacks.setdefault(dep, []):
            if plugin.enabled or dep == 'on_ready':
                func = getattr(plugin, dep)
                try:
                    await func(*args, **kwargs)
                except BaseException as e:
                    await self.log_plugin_error(plugin, e, dep, *args)

    async def on_ready(self):
        """ |coro|

            Adds a line to the log with the bot's username and id
            on a successful connection
        """

        logging.info('Connected as %s(%s)', self.user.name, self.user.id)
        presence = discord.Game(
            name='{}help to get started'.format(self.prefix),
            url='https://github.com/cheetelwin/guilty-spark'
        )

        await self.change_presence(status=presence)

        await self.call_hooks('on_ready')

    async def on_message(self, message):
        """ |coro|

            Overload of base Client's on_message event. Parses any incoming
            message for commands, and runs plugin's on_message hook
            accordingly.

        :param message:
            discord.Message Message object handed to us by discord.py
        """

        # Log the incoming message
        logging.info(
            '%s:%s:%s: %s',
            message.guild,
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
            await self.parse_command(message)
            return

        # Run all on_message hooks
        await self.call_hooks('on_message', message)

    async def on_message_delete(self, message):
        """ on_message_delete discord.py hook """
        await self.call_hooks('on_message_delete', message)

    async def on_message_edit(self, before, after):
        """ on_message_edit discord.py hook """
        await self.call_hooks('on_message_edit', before, after)

    async def on_channel_delete(self, channel):
        """ on_channel_delete discord.py hook """
        await self.call_hooks('on_channel_delete', channel)

    async def on_channel_create(self, channel):
        """ on_channel_create discord.py hook """
        await self.call_hooks('on_channel_create', channel)

    async def on_channel_update(self, before,
                                after):
        """ on_channel_update discord.py hook """
        await self.call_hooks('on_channel_update', before, after)

    async def on_member_join(self, member):
        """ on_member_join discord.py hook """
        await self.call_hooks('on_member_join', member)

    async def on_member_remove(self, member):
        """ on_member_remove discord.py hook """
        await self.call_hooks('on_member_remove', member)

    async def on_member_update(self, before, after):
        """ on_member_update discord.py hook """
        await self.call_hooks('on_member_update', before, after)

    async def on_server_join(self, server):
        """ on_server_join discord.py hook """
        await self.call_hooks('on_server_join', server)

    async def on_server_remove(self, server):
        """ on_server_remove discord.py hook """
        await self.call_hooks('on_server_remove', server)

    async def on_server_update(self, before, after):
        """ on_server_update discord.py hook """
        await self.call_hooks('on_server_update', before, after)

    async def on_server_role_create(self, role):
        """ on_server_role_create discord.py hook """
        await self.call_hooks('on_server_role_create', role)

    async def on_server_role_updated(self, before,
                                     after):
        """ on_server_role_updated discord.py hook """
        pass

    async def on_server_emojis_update(self, before,
                                      after):
        """ on_server_em discord.py hook """
        await self.call_hooks('on_server_emojis_update', before, after)

    async def on_server_available(self, server):
        """ on_server_available discord.py hook """
        await self.call_hooks('on_server_available', server)

    async def on_server_unavailable(self, server):
        """ on_server_unavailable discord.py hook """
        await self.call_hooks('on_server_unavailable', server)

    async def on_voice_state_update(self, before,
                                    after):
        """ on_voice_state_update discord.py hook """
        await self.call_hooks('on_voice_state_update', before, after)

    async def on_member_ban(self, member):
        """ on_member_ban discord.py hook """
        await self.call_hooks('on_member_ban', member)

    async def on_member_unban(self, server, user):
        """ on_member_unban discord.py hook """
        await self.call_hooks('on_member_unban', server, user)

    async def on_typing(self, channel, user,
                        when):
        """ on_typing discord.py hook """
        await self.call_hooks('on_typing', channel, user, when)

    async def on_group_join(self, channel, user):
        """ on_group_join discord.py hook """
        await self.call_hooks('on_group_join', channel, user)

    async def on_group_remove(self, channel, user):
        """ on_group_remove discord.py hook """
        await self.call_hooks('on_group_remove', channel, user)

    async def plugin_message(self, *args, **kwargs):
        """ Internal Plugin communication """
        await self.call_hooks('on_plugin_message', *args, **kwargs)
