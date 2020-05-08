"""
:Date: 2019-10-20
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import discord
import json
import random
import hashlib
from io import BytesIO
from base64 import b64decode

from guilty_spark.networking import get_bytes
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !owo'

api_image_endpoint = 'https://thisfursonadoesnotexist.com/v2/jpgs/'
image_fmt = 'seed{}.jpg'


class Waifu(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['owo'])

    async def help(self, command, message):
        embed = self.build_embed(
            title='Sound manager',
            description='UwU what\'s that?!\n\n'
                        f'**Usage**: `{self.bot.prefix}owo [seed]`\n\n'
                        '**Arguments**:'
        )

        embed.add_field(name='`seed` *Optional*', value='Seeds the random furry generator OwO')

        await self.bot.send_embed(embed)

    async def api_request(self, endpoint):
        blob = await get_bytes(endpoint)

        if not blob:
            raise FileNotFoundError()

        return blob

    async def get_trash(self, seed=None):
        if not seed:
            seed = random.rand_int(0, 99999)

        data = await self.api_request(f'{api_image_endpoint}{image_fmt.format(seed)}')

        return BytesIO(data)

    async def on_command(self, command, message: discord.Message):
        _, *args = message.content.split()

        try:
            if not args:
                image = await self.get_trash()
            else:
                hasher = hashlib.new('md5')
                hasher.update((' '.join(args)).encode())
                seed = int.from_bytes(hasher.digest()[:5], 'big')

                image = await self.get_trash(seed)

            await self.bot.send_file(message.channel, image, filename='OwO.png')

        except FileNotFoundError:
            self.bot.send_embed(self.build_embed(
                '(ó﹏ò｡)',
                'Failed to generate furry trash. Have you thrown anything out lately?',
                level=2
            ))
