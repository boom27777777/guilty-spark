"""
:Date: 2018-08-21
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----
     Plays sounds
"""
import discord
import os
import random

from guilty_spark.plugin_system.plugin import Plugin

SOUND_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sounds')


class SoundBoard(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['soundboard'])
        self.sounds = {}
        self.build_cache()

    async def help(self, command: str):
        embed = self.build_embed(
            title='Discord Soundboard',
            description='Play some sounds from my memory banks\n\n'
                        '**Usage**: `{}soundboard [subcommand]`\n\n'
                        '**Subcommands**:'.format(self.bot.prefix)
        )

        embed.add_field(
            name='`play [name]`',
            value='Plays the named sound',
            inline=False
        )

        embed.add_field(
            name='`playid [sound_id]`',
            value='Plays the sound by ID',
            inline=False
        )

        embed.add_field(
            name='`list`',
            value='Lists available sounds'
        )

        await self.bot.send_embed(embed)

    def build_cache(self):
        for file in os.listdir(SOUND_PATH):
            if file not in ['empty']:
                self.sounds[os.path.splitext(file)[0]] = file

    def get_name_by_id(self, sound_id):
        sounds = list(self.sounds)
        return sounds[sound_id]

    async def play(self, name: str):
        self.build_cache()
        try:
            name = self.sounds[name]
        except KeyError:
            return

        real_path = os.path.join(SOUND_PATH, name)
        if os.path.exists(real_path):
            command = 'ffmpeg-normalize {path} -o {path} -f'.format(path=real_path)
            os.system(command)
            await self.bot.play_sound(real_path)
        else:
            await self.bot.send_embed(self.build_embed(
                title='Error',
                description='Failed to find sound {}'.format(name),
                level=2
            ))

    async def list(self):
        self.build_cache()
        sounds = []
        for i, sound in enumerate(self.sounds, start=1):
            sounds.append('{}. {}'.format(i, sound))

        await self.bot.send_embed(self.build_embed(
            title='Available Sounds',
            description='**{}**'.format('\n'.join(sounds))
        ))

    async def on_command(self, command, message: discord.Message):
        subcommand, *args = message.content.replace(command, '').split()

        if subcommand == 'list':
            await self.list()

        elif subcommand == 'play':
            await self.play(' '.join(args))

        elif subcommand == 'playid':
            await self.play(self.get_name_by_id(int(args[0]) - 1))

        elif subcommand == 'shuffle':
            await self.play(self.get_name_by_id(
                random.randint(0, len(self.sounds) - 1)
            ))

        else:
            await self.help(command)

    async def on_plugin_message(self, *args, **kwargs):
        sound = kwargs.setdefault('soundboard-message', '')
        if sound:
            await self.play(sound)
