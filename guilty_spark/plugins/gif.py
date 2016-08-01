"""
:Date: 2016-08-01
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import asyncio
import re
import discord
import json
from random import randint
from urllib.parse import urlencode

from guilty_spark.bot import Monitor
from guilty_spark.networking import fetch_page
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !gif [search]'


class Gif(Plugin):
    def __init__(self, bot: Monitor):
        super().__init__(bot, commands=['gif'])

    @asyncio.coroutine
    def help(self):
        yield from self.bot.code(
            'Grabs a random gif for a given search term \n'
            + usage)

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        if len(message.content) > 1024:
            yield from self.bot.say(message.channel, 'Nope!')
        args = message.content.split(' ')
        if len(args) < 2:
            yield from self.bot.say(usage)
            return

        url = 'http://api.giphy.com/v1/gifs/search?' + urlencode(
            [('q', '+'.join(args[1:]))]) + '&api_key=dc6zaTOxFJmzC'
        blob = fetch_page(url)
        data = json.loads(blob.decode())
        gifs = data['data']
        gif_id = randint(0, len(gifs) - 1)
        gif = gifs[gif_id]['images']['downsized_medium']['url']
        yield from self.bot.say(gif)
