'''
:Date: 2018-01-31
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----
    Stats for @Chickenstew's discord bot
'''

import discord
import time
import os
import asyncio

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.plugin_system.data import plugin_file_path, CachedDict

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt


def gen_image():
    path = plugin_file_path('graph{}.png'.format(time.time()))
    plt.savefig(plugin_file_path(path))
    return path


def numeric(string):
    return ''.join([ch for ch in string if ch in '0123456789'])


ROBAWK_CHICKEN_ID = '401025578766958593'


class SlothStats(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['slothstats'])
        self.rolls = CachedDict('slothrolls')
        self.bonus = CachedDict('slothbonus')
        self.rates = CachedDict('slothrates')

    async def help(self, command: str):
        embed = self.build_embed(
            title='Stats for Sloths',
            description='A simple utility to help visualize sloth brutality.\n'
                        'USAGE: `{}slothstats [subcommand]`\n\n'
                        'Sub commands:'.format(self.bot.prefix),
        )
        embed.add_field(
            name='`rolls`',
            value='Shows a scatter plot of all rolls and '
                  'their frequency.\n\n',
            inline=True
        )

        embed.add_field(
            name='`bonus`',
            value='Shows the rate of MEGAWIN and TAXMAN\n\n',
            inline=True
        )

        embed.add_field(
            name='`grinder`',
            value='Shows the daily rate of sloth consumption\n\n',
            inline=True
        )

        await self.bot.send_embed(embed)

    async def on_load(self):
        await self.rolls.load()
        await self.bonus.load()
        await self.rates.load()

    async def on_ready(self):
        while True:
            await self.bot.send_message(
                content='$slothgrinder',
                destination=self.bot.get_channel('408915420557344768')
            )
            # Wait for a day
            await asyncio.sleep(24 * 60 * 60)

    def roll_plot(self):
        x_axis = list(range(1, 100))
        y_axis = []

        for i in x_axis:
            y_axis.append(self.rolls.setdefault(i, 0))

        fig = plt.figure()
        ax = fig.gca()
        ax.set_yticks(range(max(y_axis) + 1))

        plt.scatter(x_axis, y_axis)
        plt.title('Sloth Rolls')
        plt.xlabel('Results')
        plt.ylabel('Number of rolls')
        plt.grid()

    def bonus_plot(self):
        x_axis = [k for k in self.bonus]
        y_axis = []
        for i in x_axis:
            y_axis.append(self.bonus[i])

        fig = plt.figure()
        ax = fig.gca()

        if not y_axis:
            y_axis.append(0)

        ax.set_yticks(range(max(y_axis) + 1))

        plt.bar(x_axis, y_axis)
        plt.title('Sloth Bonus rolls')

    def ground_plot(self):
        x_axis = sorted([k for k in self.rates])
        y_axis = []
        for i in x_axis:
            y_axis.append(self.rates[i])

        # Calculate deltas
        x_axis = x_axis[1:]
        y_axis = [y - x for x, y in zip(y_axis[:-1], y_axis[1:])]

        if not y_axis:
            y_axis.append(0)

        average = []

        total = 0
        for i, x in enumerate(y_axis):
            if i > 0:
                total -= total / i
                total += x / i
            else:
                total = x
            average.append(total)

        plt.plot(x_axis, average, 'r--')
        plt.bar(x_axis, y_axis)
        plt.xlabel('Days')
        plt.ylabel('Ground Sloths')
        plt.title('Oh the slothmanity!')

    async def on_message(self, message: discord.Message):
        if not message.author.id == ROBAWK_CHICKEN_ID:
            return

        if message.content.startswith('Rolled'):
            _, raw_result, *_ = message.content.split()
            raw_result = ''.join([ch for ch in raw_result if ch in '0123456789'])
            try:
                result = int(raw_result)
                self.rolls.setdefault(result, 0)
                self.rolls[result] += 1
                await self.rolls.cache()
            except ValueError:
                return

        if 'TAXMAN' in message.content:
            self.bonus.setdefault('TAXMAN', 0)
            self.bonus['TAXMAN'] += 1
            await self.bonus.cache()

        if 'MEGAWIN' in message.content:
            self.bonus.setdefault('MEGAWIN', 0)
            self.bonus['MEGAWIN'] += 1
            await self.bonus.cache()

        if 'sloths have been thrown to the grinder' in message.content:
            sloths, *_ = message.content.split()
            try:
                sloths = int(numeric(sloths))
                self.rates[time.strftime('%Y-%m-%d')] = sloths
                await self.rates.cache()
            except ValueError:
                return

    async def send_image(self, message):
        image_path = gen_image()
        await self.bot.send_file(message.channel, image_path)
        os.remove(image_path)

    async def on_command(self, command, message: discord.Message):
        sub_command, *args = message.content.replace(command, '').split()
        if sub_command == 'rolls':
            self.roll_plot()
            await self.send_image(message)

        if sub_command == 'bonus':
            self.bonus_plot()
            await self.send_image(message)

        if sub_command == 'grinder':
            self.ground_plot()
            await self.send_image(message)
