"""
:Date: 2016-08-03
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import discord

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin


class PluginAdmin(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['plugin'])

    async def help(self, command: str):
        embed = self.build_embed(
            title='Plugin Administration',
            description='Disable and enable plugins\n\n'
                        '**Usage**: `{}plugin [subcommand]`\n\n'
                        '**Subcommands**:'.format(self.bot.prefix)
        )

        embed.add_field(
            name='`list`',
            value='Shows the current state of plugins for this channel',
            inline=False
        )

        embed.add_field(
            name='`enable [plugin_name]`',
            value='Enables the plugin for this channel',
            inline=False
        )

        embed.add_field(
            name='`disable [plugin_name]`',
            value='Disables a plugin for this channel',
            inline=False
        )

        await self.bot.send_embed(embed)

    async def _get_plugins(self, name):
        try:
            return self.bot.plugins[name]
        except KeyError:
            await self.bot.say('Plugin {} not found'.format(name))
            raise

    async def enable_plugin(self, name: str, message: discord.Message):
        handler = await self._get_plugins(name)
        if handler and not handler.enabled or handler.use_whitelist:
            if handler.use_whitelist:
                handler.disable(message.channel.id)
            else:
                handler.enable(message.channel.id)
            await handler.cache()

            await self.bot.say('Plugin {} enabled'.format(name))
        else:
            await self.bot.say('Plugin {} already enabled'.format(name))

    async def disable_plugin(self, name: str, message: discord.Message):
        handler = await self._get_plugins(name)
        if handler.enabled or handler.use_whitelist:
            if handler.use_whitelist:
                handler.enable(message.channel.id)
            else:
                handler.disable(message.channel.id)
            await handler.cache()

            await self.bot.say('Disabled {} for channel {}'.format(
                name, message.channel
            ))
        else:
            await self.bot.say('Plugin {} already disabled'.format(name))

    @Plugin.admin
    async def on_command(self, command, message: discord.Message):
        args = message.content.split()

        if len(args) < 2:
            sub_command = 'list'
        else:
            _, sub_command, *args = args

        if sub_command == 'list':
            p_list = []
            for name, handle in self.bot.plugins.items():
                p_list.append('{:<20}{:<10}{}'.format(
                    name,
                    'Enabled' if handle.enabled else 'Disabled',
                    'Whitelisted' if handle.use_whitelist else ''
                ))
            await self.bot.code('\n'.join(p_list))

        if sub_command == 'disable':
            for name in args:
                try:
                    await self.disable_plugin(name, message)
                except KeyError:
                    continue

        if sub_command == 'enable':
            for name in args:
                try:
                    await self.enable_plugin(name, message)
                except KeyError:
                    continue
