"""
:Date: 2019-06-11
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import discord
from PIL import Image
import io

from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.networking import get


class Braille(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['braille'])

    async def to_braille(self, url):
        image = Image.open(io.BytesIO(await get(url)))

        print(image)

    async def on_command(self, command, message: discord.Message):
        url, *_ = message.content.replace(command, '').split()
        if url:
            await self.bot.say(await self.to_braille(url))

