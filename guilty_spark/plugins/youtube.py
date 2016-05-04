import asyncio
import re
import discord
from urllib.parse import urlencode

from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.networking import fetch_page

usage = 'Usage: !youtube [search]'


class Youtube(Plugin):
    commands = ['youtube']

    @asyncio.coroutine
    def help(self):
        yield from self.bot.say(
            'Grabs the first related youtube video for a given search \n' \
            + usage)

    @asyncio.coroutine
    def on_command(self, message: discord.Message):
        if len(message.content) > 1024:
            yield from self.bot.say(message.channel, 'Nope!')
        args = message.content.split(' ')
        if len(args) < 2:
            yield from self.bot.say(usage)
            return

        url = 'https://www.youtube.com/results?' + urlencode(
            [('search_query', '+'.join(args[1:]))])
        html = fetch_page(url)
        links = re.findall('<a href="(\/watch\?v=[^"]+)"', html.decode())
        if links:
            link = 'http://youtube.com' + links[0]
            yield from self.bot.say(link)
        return
