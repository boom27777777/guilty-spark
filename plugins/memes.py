import asyncio
import discord
import re
import os
import yaml

from guilty_spark import get_resource
from guilty_spark.plugin_system.data import CachedDict, plugin_file
from guilty_spark.plugin_system.plugin import Plugin

usage = '''-Usage:
+    !bindmeme [in/is/re]||[trigger]||[meme]
+    !unbindmeme [trigger]
+    !listmemes
+    !searchmemes [trigger]

-Admin Commands:
+    !linkmemes [server_id]
+    !unlinkmemes
+    !copymemes [server_id]'''


class Memes(Plugin):
    def __init__(self, name, bot):
        super().__init__(
            name, bot, commands=[
                'bindmeme',
                'unbindmeme',
                'listmemes',
                'searchmemes',
                'copymemes',
                'linkmemes',
                'unlinkmemes',
            ]
        )
        self._memes = CachedDict('shitposts')
        self.server_id = 0

    async def _migrate_memes(self):
        try:
            with plugin_file('shitpost.yml') as memes:
                old_memes = yaml.load(memes)
                if not old_memes:
                    return
                for key, value in old_memes.items():
                    self._memes[key] = value
            await self.cache_memes()
            os.remove(get_resource('plugin_data', 'shitpost.yml'))
        except IOError:
            return

    async def on_load(self):
        await super().on_load()
        await self._memes.load()
        await self._migrate_memes()

    @property
    def memes(self):
        try:
            return self._memes[self.server_id]
        except KeyError:
            self._memes[self.server_id] = {
                'in': {},
                'is': {},
                're': {},
                'link': None,
            }
            return self._memes[self.server_id]

    async def cache_memes(self):
        await self._memes.cache()

    async def delete_meme(self, trigger: str):
        for key in self.memes:
            if not self.memes[key]:
                continue
            if trigger in self.memes[key]:
                del self.memes[key][trigger]
                await self.cache_memes()
                return True
        return False

    async def copy_memes_from(self, old_id):
        for type in self._memes[old_id]:
            for trigger, meme in self._memes[old_id][type].items():
                self.memes[type][trigger] = meme

        await self.cache_memes()

    async def help(self, _):
        await self.bot.code(
            '\n'.join([
                '-Retune the dank emitters to recognize new memes\n',
                usage + '\n',
                '-Triggers:',
                '+    in: trigger is anywhere in the message',
                '+    is: message is exactly equal to trigger',
                '+    re: RegEx matching on message (python flavored)\n',
                '-I also support various tags you can use:',
                '+    <user>    | The user that triggered the message',
                '+    <channel> | The channel the message was triggered in',
                '+    <server>  | The server the message was triggered in\n',
                '-Examples:',
                '+    !bindmeme is||kthx||bai <user>',
                '+    !bindmeme re||(?i)regex||Case insensitive meme!',
            ]), language='diff')
        return

    async def bind_meme(self, content: str):
        content = content.replace(self.bot.prefix + 'bindmeme', '')
        args = content.split('||')
        if len(args) != 3:
            await self.bot.code(usage)
            return
        meme_type, trigger, meme = [a.strip() for a in args]
        if meme_type not in ['in', 'is', 're']:
            await self.bot.code(usage)
            return
        if len(trigger) < 3:
            await self.bot.say('Trigger needs to be more then 3 characters')
            return
        if trigger.startswith(self.bot.prefix):
            await self.bot.say(
                'Trigger can\'t begin with "{}"'.format(self.bot.prefix))

        try:
            self.memes[meme_type][trigger] = meme
        except KeyError:
            self.memes[meme_type] = {}
            self.memes[meme_type][trigger] = meme

        await self.cache_memes()
        await self.bot.say('Meme bound')

    async def unbind_meme(self, content: str):
        content = content.replace(self.bot.prefix + 'unbindmeme', '')
        arg = content.strip()

        if not arg:
            await self.bot.code(usage)

        deleted = await self.delete_meme(arg)
        if deleted:
            await self.bot.say('Meme unbound')
        else:
            await self.bot.say('You have given me stale memes')
        return

    async def list_memes(self):
        memes = []
        for section, data in self.memes.items():
            memes.append('\n- {:_^25} \n'.format(section))
            if not data:
                continue

            for trigger, dank in data.items():
                memes.append('+ {:<25} | {}'.format(trigger, dank))

        memes = '\n'.join(memes)

        links = re.findall(r'[^<](http[^ \n]+)', memes)

        replaced = []
        for link in links:
            if link not in replaced:
                memes = memes.replace(link, '<{}>'.format(link))
            replaced.append(link)

        memes = memes.replace('```', '')

        await self.bot.code(memes, language='diff')

    @staticmethod
    def format_tag(autism: str, message: discord.Message):
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

        if self.memes.setdefault('link', None):
            self.server_id = self.memes['link']

    def get_meme(self, message: str):
        memes = self.memes
        dank = ""
        maymay = ""
        if message in memes['is']:
            dank = memes['is'][message]
            maymay = message

        else:
            for meme, autism in memes['in'].items():
                if meme in message:
                    dank = autism
                    maymay = meme

            for meme, autism in memes['re'].items():
                try:
                    if re.search(meme, message):
                        dank = autism
                        maymay = meme
                except:
                    self.delete_meme(meme)
        return dank, maymay

    async def search_memes(self, content):
        shit_post = ' '.join(content.split()[1:])
        if not content:
            await self.bot.code(usage)
            return

        memes = self.memes
        steaming_load = []
        for meme, autism in memes['is'].items():
            if meme == shit_post:
                steaming_load.append('[is] {:<25}| {}'.format(meme, autism))

        for meme, autism in memes['in'].items():
            if meme in shit_post:
                steaming_load.append('[in] {:<25}| {}'.format(meme, autism))

        for meme, autism in memes['is'].items():
            try:
                if re.search(meme, shit_post):
                    steaming_load.append('[re] {:<25}| {}'.format(meme, autism))
            except:
                await self.delete_meme(meme)

        steaming_load = '+' + '\n-'.join(steaming_load).replace('```', '')
        await self.bot.code(steaming_load, language='diff')

    async def copy_memes(self, message: discord.Message):
        if int(message.author.id) != self.bot.settings['owner']:
            await self.bot.say(
                'Sorry only <@{}> has that power'.format(
                    self.bot.settings['owner']
                ))
            return
        try:
            await self.copy_memes_from(
                message.content.split()[1]
            )
            await self.bot.say('The deed is done.')
        except BaseException:
            await self.bot.say('Something went wrong!')

    async def link_memes(self, message):
        try:
            _, link_id = message.content.split()
        except ValueError:
            await self.bot.say('You must use the link force')
            return

        if int(message.author.id) != self.bot.settings['owner']:
            await self.bot.say(
                'Sorry only <@{}> has that power'.format(
                    self.bot.settings['owner']
                ))
            return
        elif link_id not in self._memes:
            await self.bot.say(
                'I can\'t find a server with the id of {}'.format(link_id)
            )
        else:
            self.memes['link'] = link_id
            await self.bot.say('Meme bridge established.')

    async def unlink_memes(self, message):
        if int(message.author.id) != self.bot.settings['owner']:
            await self.bot.say(
                'Sorry only <@{}> has that power'.format(
                    self.bot.settings['owner']
                ))
            return
        elif self.memes.setdefault('link', None):
            self.memes.pop('link', None)
            await self.bot.say('Meme bridge terminated')
        else:
            await self.bot.say('No meme bridge detected.')

    async def on_command(self, command, message: discord.Message):
        self.set_server_id(message)

        command = command[1:]
        if 'bindmeme' == command:
            await self.bind_meme(message.content)

        elif 'unbindmeme' == command:
            await self.unbind_meme(message.content)

        elif 'listmemes' == command:
            await self.list_memes()

        elif 'searchmemes' == command:
            await self.search_memes(message.content)

        elif 'copymemes' == command:
            await self.copy_memes(message)

        elif 'linkmemes' == command:
            await self.link_memes(message)

        elif 'unlinkmemes' == command:
            await self.unlink_memes(message)

    async def on_message(self, message: discord.Message):
        self.set_server_id(message)

        dank, _ = self.get_meme(message.content)

        if dank:
            if re.search(r'<(user|channel|server)>', dank):
                dank = self.format_tag(dank, message)

            if dank.startswith('<speak>'):
                await self.bot.plugin_message(**{
                    'speak-message': dank.replace('<speak>', ''),
                    'user': message.author
                })

            else:
                await self.bot.say(dank)
