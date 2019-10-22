"""
:Date: 2018-07-06
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import discord

from random import randint

from guilty_spark.plugin_system.data import CachedDict
from guilty_spark.plugin_system.plugin import Plugin


class Thanos(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['thanos'])

        self.list = CachedDict('thanosdidnothingwrong')

    async def help(self, command, message):
        embed = self.build_embed(
            title='Face Thanos\' judgement',
            description='Sub commands:\n'
                        '  `list`  Remember the fallen'
        )
        await self.bot.send_embed(embed)

    async def on_load(self):
        await self.list.load()

    async def judge(self, user):
        if user not in self.list:
            self.list[user] = randint(1, 100) >= 50
            await self.list.cache()

        return self.list[user]

    async def show_list(self, server: discord.Server):
        alive = []
        fallen = []
        for user in self.list:
            name = server.get_member(user)

            if not name:
                continue

            name = name.display_name

            if self.list[user]:
                alive.append(name)
            else:
                fallen.append(name)

        await self.bot.say(
            'Those who still live:\n' +
            ', '.join(alive) +
            '\n\nThose who sacrificed everything for a better universe:\n' +
            ', '.join(fallen)
        )

    async def on_command(self, command, message: discord.Message):
        sub_command = message.content.replace(command, '').strip()

        if sub_command == 'list':
            await self.show_list(message.server)
        else:
            if await self.judge(message.author.id):
                await self.bot.say('You were spared by Thanos.')

            else:
                await self.bot.say('You were slain by Thanos, for the good of the Universe.')
