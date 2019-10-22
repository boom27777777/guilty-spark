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

from guilty_spark.networking import post
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !waifu'

api_generate_endpoint = 'https://api.waifulabs.com/generate'
api_big_endpoint = 'https://api.waifulabs.com/generate_big'


class Waifu(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['waifu'])

    async def help(self, command, message):
        embed = self.build_embed(
            title='Sound manager',
            description='Generates a Waifu using the weeb AI at https://waifulabs.com\n\n'
                        f'**Usage**: `{self.bot.prefix}waifu [seed]`\n\n'
                        '**Arguments**:'
        )

        embed.add_field(name='`seed` *Optional*', value='Seeds the random waifu generator OwO')

        await self.bot.send_embed(embed)

    async def api_request(self, endpoint, payload):
        blob = await post(endpoint, json.dumps(payload))

        if not blob:
            raise FileNotFoundError()

        return json.loads(blob)

    async def generate_seeds(self, seed=1000000):
        return [seed for _ in range(17)] + [[0 for _ in range(3)]]

    async def get_waifu(self, seed=None):
        if seed:
            payload = {'currentGirl': await self.generate_seeds(seed), 'step': 3}
        else:
            payload = {'step': 0}

        data = await self.api_request(api_generate_endpoint, payload)

        girl = data.get('newGirls')[0].get('image')

        return BytesIO(b64decode(girl))

    async def on_command(self, command, message: discord.Message):
        _, *args = message.content.split()

        try:
            if not args:
                image = await self.get_waifu()
            else:
                hasher = hashlib.new('md5')
                hasher.update((' '.join(args)).encode())
                seed = int.from_bytes(hasher.digest()[:4], 'big')

                image = await self.get_waifu(seed)

            await self.bot.send_file(message.channel, image, filename='waifu.png')

        except FileNotFoundError:
            self.bot.send_embed(self.build_embed(
                '(ó﹏ò｡)',
                'Failed to generate Waifu... I\'m sorry senpai...',
                level=2
            ))
