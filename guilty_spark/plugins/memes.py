import asyncio
import discord
import yaml
import re

from guilty_spark.plugin_system.data import plugin_file
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage:\n' \
        '\t!bindmeme [in/is]::[trigger]::[meme]\n' \
        '\t!unbindmeme [trigger]\n' \
        '\t!listmemes'


class Memes(Plugin):
    def __init__(self, bot):
        super().__init__(bot, commands=['bindmeme', 'unbindmeme', 'listmemes'])
        self._memes = {}
        self.server_id = 0
        self.load_memes()

    @property
    def memes(self):
        try:
            return self._memes[self.server_id]
        except KeyError:
            self._memes[self.server_id] = {
                'in': {},
                'is': {},
                're': {}
            }
            return self._memes[self.server_id]

    def load_memes(self):
        try:
            with plugin_file('shitpost.yml') as memes:
                self._memes = yaml.load(memes)
        except IOError:
            pass

    def cache_memes(self):
        with plugin_file('shitpost.yml', 'w') as memes:
            yaml.dump(self._memes, memes, default_flow_style=False)

    def delete_meme(self, trigger: str):
        for key in self.memes:
            if trigger in self.memes[key]:
                del self.memes[key][trigger]
                self.cache_memes()
                return True
        return False

    def help(self):
        yield from self.bot.say(
            ('```Retune the dank emitters to include new autism\n\n{}\n\n'
             'in: trigger is anywhere in the message\n'
             'is: is exactly equal to trigger\n'
             're: RegEx matching\n\n'
             'I also support various tags you can use:\n'
             '<user>    | The user that triggered the message\n'
             '<channel> | The channel the message was triggered in\n'
             '<server>  | The server the message was triggered in\n'
             'Example:\n'
             '\t!bindmeme is::kthx::bai <user>```'
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
        if trigger.startswith(self.bot.prefix):
            yield from self.bot.say(
                'Trigger can\'t begin with "{}"'.format(self.bot.prefix))

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

    def list_memes(self):
        memes = yaml.dump(self.memes, default_flow_style=False)

        links = re.findall(r'[^<](http[^ \n]+)', memes)

        replaced = []
        for link in links:
            if link not in replaced:
                memes = memes.replace(link, '<{}>'.format(link))
            replaced.append(link)

        if len(memes) > 2000:
            index = 0
            while len(memes) - index > 2000:
                chunk = memes[index: index + 2000]
                yield from self.bot.code(chunk)
                index += 2000
            yield from self.bot.code(memes[index:])
        else:
            yield from self.bot.code(memes)

    def format_tag(self, autism: str, message: discord.Message):
        if '<user>' in autism:
            autism = autism.replace('<user>', message.author.display_name)

        if '<channel>' in autism:
            autism = autism.replace('<channel>', str(message.channel))

        if '<server>' in autism:
            autism = autism.replace('<server>', str(message.server))

        return autism

    def set_server_id(self, message: discord.Message):
        if message.server:
            self.server_id = message.server.id
        else:
            self.server_id = message.channel.id

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        self.set_server_id(message)
        command = command[1:]
        if 'bindmeme' == command:
            yield from self.bind_meme(message.content)

        if 'unbindmeme' == command:
            yield from self.unbind_meme(message.content)

        if 'listmemes' == command:
            yield from self.list_memes()

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        self.set_server_id(message)

        memes = self.memes
        dank = None
        if message.content in memes['is']:
            dank = memes['is'][message.content]

        else:
            for meme, autism in memes['in'].items():
                if meme in message.content:
                    dank = autism

            for meme, autism in memes['re'].items():
                if re.search(meme, message.content):
                    dank = autism

        if dank:
            if re.search(r'<(user|channel|server)>', dank):
                dank = self.format_tag(dank, message)

            yield from self.bot.say(dank)
