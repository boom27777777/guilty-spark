import asyncio
import discord
import yaml
import re

from guilty_spark.plugin_system.data import plugin_file
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage:\n' \
        '\t!bindmeme [in/is]::[trigger]::[meme]\n' \
        '\t!unbindmeme [trigger]'


class Memes(Plugin):
    def __init__(self, bot):
        super().__init__(bot, commands=['bindmeme', 'undbindmeme'])
        self.memes = {
            'in': {},
            'is': {},
            're': {}
        }
        self.load_memes()

    def load_memes(self):
        try:
            with plugin_file('shitpost.yml') as memes:
                self.memes = yaml.load(memes)
        except IOError:
            pass

    def cache_memes(self):
        with plugin_file('shitpost.yml', 'w') as memes:
            yaml.dump(self.memes, memes, default_flow_style=False)

    def delete_meme(self, trigger: str):
        for key in self.memes:
            if trigger in self.memes[key]:
                del self.memes[key][trigger]
                self.cache_memes()
                return True
        return False

    def help(self):
        yield from self.bot.say(
            ('Retune the dank emitters to include new autism\n\n{}\n\n'
             'in: trigger is anywhere in the message\n'
             'is: is exactly equal to trigger\n'
             're: RegEx matching\n'
             'Example:\n'
             '\t!bindmeme is::kthx::bai'
             ).format(usage))
        return

    def bind_meme(self, content: str):
        content = content.replace(self.bot.prefix + 'bindmeme', '')
        args = content.split('::')
        if len(args) != 3:
            yield from self.bot.say(usage)
            return
        meme_type, trigger, meme = [a.strip() for a in args]
        if meme_type not in ['in', 'is', 're']:
            yield from self.bot.say(usage)
            return
        if len(trigger) < 3:
            yield from self.bot.say('Trigger needs to be more then 3 characters')
            return

        try:
            self.memes[meme_type][trigger] = meme
        except KeyError:
            self.memes[meme_type] = {}
            self.memes[meme_type][trigger] = meme

        self.cache_memes()
        yield from self.bot.say('Meme bound')
        return

    def unbind_meme(self, content: str):
        content = content.replace(self.bot.prefix + 'unbindmeme', '')
        arg = content.strip()

        if not arg:
            yield from self.bot.say(usage)

        if self.delete_meme(arg):
            yield from self.bot.say('Meme unbound')
        else:
            yield from self.bot.say('You have given me stale memes')
        return

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        if self.bot.prefix + 'bindmeme' == command:
            yield from self.bind_meme(message.content)

        if self.bot.prefix + 'unbindmeme' == command:
            yield from self.unbind_meme(message.content)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        memes = self.memes
        if message.content in memes['is']:
            yield from self.bot.say(memes['is'][message.content])
            return

        for meme, autism in memes['in'].items():
            if meme in message.content:
                yield from self.bot.say(autism)
                return

        for meme, autism in memes['re'].items():
            if re.search(meme, message.content):
                yield from self.bot.say(autism)
                return
