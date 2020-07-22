import asyncio

import datetime
import discord

from guilty_spark.plugin_system.data import CachedDict


class Plugin:
    """ Base plugin class """

    def __init__(self, name, bot, commands=None):
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
    def build_embed(title= None, description= None,
                    fields= None,
                    thumbnail= 'https://i.imgur.com/rJYfMZk.png',
                    level= 0):
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
    def has_permissions(user, hook):
        if hasattr(hook, 'perm_admin'):
            if user.guild_permissions.administrator:
                return True
            else:
                return False

        elif not hasattr(user, 'server_permissions'):
            return True

        else:
            return True

    def on_ready(self):
        """ on_ready discord.py hook """
        pass

    def on_message(self, message):
        """ on_message discord.py hook """
        pass

    def on_command(self, command, message):
        """ on_command discord.py hook """
        pass

    def on_message_delete(self, message):
        """ on_message_delete discord.py hook """
        pass

    def on_message_edit(self, before, after):
        """ on_message_edit discord.py hook """
        pass

    def on_channel_delete(self, channel):
        """ on_channel_delete discord.py hook """
        pass

    def on_channel_create(self, channel):
        """ on_channel_create discord.py hook """
        pass

    def on_channel_update(self, before,
                          after):
        """ on_channel_update discord.py hook """
        pass

    def on_member_join(self, member):
        """ on_member_join discord.py hook """
        pass

    def on_member_remove(self, member):
        """ on_member_remove discord.py hook """
        pass

    def on_member_update(self, before, after):
        """ on_member_update discord.py hook """
        pass

    def on_server_join(self, server):
        """ on_server_join discord.py hook """
        pass

    def on_server_remove(self, server):
        """ on_server_remove discord.py hook """
        pass

    def on_server_update(self, before, after):
        """ on_server_update discord.py hook """
        pass

    def on_server_role_create(self, role):
        """ on_server_role_create discord.py hook """
        pass

    def on_server_role_updated(self, before,
                               after):
        """ on_server_role_updated discord.py hook """
        pass

    def on_server_emojis_update(self, before,
                                after):
        """ on_server_em discord.py hook """
        pass

    def on_server_available(self, server):
        """ on_server_available discord.py hook """
        pass

    def on_server_unavailable(self, server):
        """ on_server_unavailable discord.py hook """
        pass

    def on_voice_state_update(self, before,
                              after):
        """ on_voice_state_update discord.py hook """
        pass

    def on_member_ban(self, member):
        """ on_member_ban discord.py hook """
        pass

    def on_member_unban(self, server, user):
        """ on_member_unban discord.py hook """
        pass

    def on_typing(self, channel, user,
                  when):
        """ on_typing discord.py hook """
        pass

    def on_group_join(self, channel, user):
        """ on_group_join discord.py hook """
        pass

    def on_group_remove(self, channel, user):
        """ on_group_remove discord.py hook """
        pass

    def on_plugin_message(self, *args, **kwargs):
        """ Internal plugin message passing """
        pass

    async def help(self, command, message):
        await self.bot.say("Help hasn't been added for this command yet")

    def __repr__(self):
        return self.name
