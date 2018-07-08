"""
:Date: 2018-07-07
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import discord

from guilty_spark.plugin_system.plugin import Plugin


class Sound(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['sound'])

    async def help(self, msg):
        embed = self.build_embed(
            title='Sound manager',
            description='Manages outing sounds'
        )

        embed.add_field('commands', '`stop` stop running sounds')

        await self.bot.send_embed(embed)

    async def on_command(self, command, message: discord.Message):
        if 'stop' in message.content:
            await self.bot.stop_sound(message.author)
