import asyncio
import re
from urllib.parse import urlencode

from guilty_spark.application import bot
from guilty_spark.networking import fetch_page

@asyncio.coroutine
def on_message(message):
    if '!youtube' in message.content:
        if len(message.content) > 1024:
            yield from bot.send_message(message.channel, 'Nope!')
        args = message.content.split(' ')
        if len(args) < 2:
            yield from bot.send_message(message.channel, 'Usage: !youtube [search]')
            return

        url = 'https://www.youtube.com/results?' + urlencode(
            [('search_query', '+'.join(args[1:]))])
        html = fetch_page(url)
        links = re.findall('<a href="(\/watch\?v=[^"]+)"', html.decode())
        if links:
            link = 'http://youtube.com' + links[0]
            yield from bot.send_message(message.channel, link)
        return
