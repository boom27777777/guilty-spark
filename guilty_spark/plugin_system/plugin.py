import asyncio

import datetime
import discord

from guilty_spark.plugin_system.data import CachedDict


class Plugin:
    """ Base plugin class """

    def __init__(self, name: str, bot, commands=None):
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

        methods = [m for m in dir(self) if m.startswith('on_')]
        for dep in methods:
            method = self.__getattribute__(dep)
            if asyncio.iscoroutinefunction(method):
                self.depends.append(dep)

        self._cache = CachedDict(self.name)
        self.disabled_channels = []
        self.use_whitelist = False

    async def on_load(self):
        data = await self._cache.load()

        if not data or not self._cache.setdefault('disabled_channels', []):
            self._cache['disabled_channels'] = []

        self.disabled_channels = self._cache['disabled_channels']

    async def cache(self):
        await self._cache.cache()

    def disable(self, channel_id):
        self.disabled_channels.append(channel_id)

    def enable(self, channel_id):
        self.disabled_channels.remove(channel_id)

    @property
    def enabled(self):
        if self.bot.current_message:
            chan_id = self.bot.current_message.channel.id
            if not self.use_whitelist and chan_id not in self.disabled_channels:
                return True
            elif self.use_whitelist and chan_id in self.disabled_channels:
                return True
        return False

    @staticmethod
    def build_embed(title: str = None, description: str = None,
                    fields: dict = None,
                    thumbnail: str = 'https://i.imgur.com/rJYfMZk.png',
                    level: int = 0):
        """ A wrapper for Discord's ritch embed system

        :param title:
            Title of embed
        :param description:
            Body of embed
        :param fields:
            A dict of title/descriptions
        :param thumbnail:
            Optional post thumbnail
        """

        colors = {
            0: 0x227C22,
            1: 0x7C7C00,
            2: 0xFF2B2B,
        }

        embed = discord.Embed(
            title=title,
            description=description,
            color=colors[level]
        )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if fields:
            for k, v in fields.items():
                embed.add_field(name=k, value=v)

        return embed

    @staticmethod
    def admin(func):
        func.perm_admin = True
        return func

    @staticmethod
    def has_permissions(user: discord.User, hook):
        if not hasattr(user, 'server_permissions'):
            return True

        elif hasattr(hook, 'perm_admin'):
            if user.server_permissions.administrator:
                return True
            else:
                return False

        else:
            return True

    def on_ready(self):
        """ on_ready discord.py hook """
        pass

    def on_message(self, message: discord.Message):
        """ on_message discord.py hook """
        pass

    def on_command(self, command, message: discord.Message):
        """ on_command discord.py hook """
        pass

    def on_message_delete(self, message: discord.Message):
        """ on_message_delete discord.py hook """
        pass

    def on_message_edit(self, before: discord.Message, after: discord.Message):
        """ on_message_edit discord.py hook """
        pass

    def on_channel_delete(self, channel: discord.Channel):
        """ on_channel_delete discord.py hook """
        pass

    def on_channel_create(self, channel: discord.Channel):
        """ on_channel_create discord.py hook """
        pass

    def on_channel_update(self, before: discord.Channel,
                          after: discord.Channel):
        """ on_channel_update discord.py hook """
        pass

    def on_member_join(self, member: discord.Member):
        """ on_member_join discord.py hook """
        pass

    def on_member_remove(self, member: discord.Member):
        """ on_member_remove discord.py hook """
        pass

    def on_member_update(self, before: discord.Member, after: discord.Member):
        """ on_member_update discord.py hook """
        pass

    def on_server_join(self, server: discord.Server):
        """ on_server_join discord.py hook """
        pass

    def on_server_remove(self, server: discord.Server):
        """ on_server_remove discord.py hook """
        pass

    def on_server_update(self, before: discord.Server, after: discord.Server):
        """ on_server_update discord.py hook """
        pass

    def on_server_role_create(self, role: discord.Role):
        """ on_server_role_create discord.py hook """
        pass

    def on_server_role_updated(self, before: discord.Role,
                               after: discord.Role):
        """ on_server_role_updated discord.py hook """
        pass

    def on_server_emojis_update(self, before: discord.Server,
                                after: discord.Server):
        """ on_server_em discord.py hook """
        pass

    def on_server_available(self, server: discord.Server):
        """ on_server_available discord.py hook """
        pass

    def on_server_unavailable(self, server: discord.Server):
        """ on_server_unavailable discord.py hook """
        pass

    def on_voice_state_update(self, before: discord.Member,
                              after: discord.Member):
        """ on_voice_state_update discord.py hook """
        pass

    def on_member_ban(self, member: discord.Member):
        """ on_member_ban discord.py hook """
        pass

    def on_member_unban(self, server: discord.Server, user: discord.User):
        """ on_member_unban discord.py hook """
        pass

    def on_typing(self, channel: discord.Channel, user: discord.User,
                  when: datetime.datetime):
        """ on_typing discord.py hook """
        pass

    def on_group_join(self, channel: discord.Channel, user: discord.User):
        """ on_group_join discord.py hook """
        pass

    def on_group_remove(self, channel: discord.Channel, user: discord.User):
        """ on_group_remove discord.py hook """
        pass

    def on_plugin_message(self, *args, **kwargs):
        """ Internal plugin message passing """
        pass

    async def help(self, command: str, message):
        await self.bot.say("Help hasn't been added for this command yet")

    def __repr__(self):
        return self.name
