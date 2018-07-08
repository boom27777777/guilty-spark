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

    async def set_volume(self, to_set):
        try:
            new_vol = float(to_set) / 100.0
            if new_vol > 1.0 or new_vol < 0.0:
                raise ValueError

            self.bot.set_volume(new_vol)
        except ValueError:
            await self.bot.send_embed(self.build_embed(
                title='Error',
                description='Failed to set Volume to {} '
                            'only 0-100 allowed'.format(to_set),
                level=2
            ))

    async def on_command(self, command, message: discord.Message):
        _, *args = message.content.split()

        if len(args) == 0:
            await self.help(message)

        elif args[0] == 'stop':
            await self.bot.stop_sound(message.author)

        elif args[0] == 'volume':
            if len(args) == 2:
                await self.set_volume(args[1])
            else:
                await self.bot.send_embed(self.build_embed(
                    title='Sound Volume',
                    description='```{:.0}/100```'.format(
                        self.bot.get_volume() * 100.0)
                ))
