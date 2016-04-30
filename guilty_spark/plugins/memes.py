import asyncio

import discord
import yaml
import re
from guilty_spark.plugin_system.plugin import BasePlugin

usage = 'Usage:\n' \
        '\t!bindmeme [in/is]::[trigger]::[meme]\n' \
        '\t!unbindmeme [trigger]'


class Memes(BasePlugin):
    commands = ['bindmeme', 'undbindmeme']

    def __init__(self, bot):
        super().__init__(bot)

        try:
            with open('shitpost.yml') as memes:
                self.dreams = yaml.load(memes)
        except IOError:
            self.dreams = {
                'memes':
                    {
                        'in': {},
                        'is': {},
                        're': {}
                    }
            }

    def cache_memes(self):
        with open('shitpost.yml', 'w') as memes:
            yaml.dump(self.dreams, memes, default_flow_style=False)

    def delete_meme(self, trigger: str):
        for key in self.dreams:
            if trigger in self.dreams[key]:
                del self.dreams[key][trigger]
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
        content = content.replace('!bindmeme', '')
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
            self.dreams[meme_type][trigger] = meme
        except KeyError:
            self.dreams[meme_type] = {}
            self.dreams[meme_type][trigger] = meme

        self.cache_memes()
        yield from self.bot.say('Meme bound')
        return

    def unbind_meme(self, content: str):
        content = content.replace('!unbindmeme', '')
        arg = content.strip()

        if self.delete_meme(arg):
            yield from self.bot.say('Meme unbound')
        else:
            yield from self.bot.say('You have given me stale memes')
        return

    @asyncio.coroutine
    def on_command(self, message: discord.Message):
        if 'bindmeme' in message.content:
            self.bind_meme(message.content)

        if 'unbindmeme' in message.content:
            self.unbind_meme(message.content)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        memes = self.dreams
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
