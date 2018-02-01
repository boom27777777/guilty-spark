"""
:Date: 2018-01-31
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----
    Stats for @Chickenstew's discord bot
"""

import discord
import matplotlib.pyplot as plt
import time
import os

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.plugin_system.data import plugin_file_path, CachedDict


def gen_image():
    path = plugin_file_path('graph{}.png'.format(time.time()))
    plt.savefig(plugin_file_path(path))
    return path


class SlothStats(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['slothstats'])
        self.rolls = CachedDict('slothrolls')
        self.bonus = CachedDict('slothbonus')

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
        ax.set_yticks(range(max(y_axis) + 1))

        plt.bar(x_axis, y_axis)
        plt.title('Sloth Bonus rolls')

    async def on_message(self, message: discord.Message):
        if not message.author.id == '401025578766958593':
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


