"""
:Date: 2019-06-10
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----


Usage
-----
    ``$ python logging``
"""

from guilty_spark.plugin_system.plugin import Plugin


class SoundBoard(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['logging'])
        self.use_whitelist = True

    async def help(self, command: str, message):
        embed = self.build_embed(
            title='Discord logging',
            description='Comprehensive server auditing\n\n'
                        '**Usage**: `{}logging`\n\n'.format(self.bot.prefix)
        )

        embed.add_field(
            name='`toggle`',
            value='Enables or disables logging',
            inline=False
        )

        await self.bot.send_embed(embed)
