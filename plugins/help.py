import asyncio
import discord

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !help [command]'


class Help(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['help'])
        self._longest = 0
        self._padding = ''

    async def help(self, _):
        await self.bot.code('Gives you helps \n' + usage)

    @property
    def _plugins(self):
        return sorted(self.bot.plugins.items(), key=lambda x: x[0])

    def _row_format(self):
        longest = max([len(p) for p in self.bot.plugins])
        if longest != self._longest:
            self._longest = longest
            self._padding = ' ' * (longest + 4)

        name_fmt = '  {{:>{}}}: '.format(self._longest)
        return name_fmt

    def _plugin_cmds(self, name, plug, name_fmt):
        cmds = []
        for cmd in plug.commands:
            command = self.bot.prefix + cmd

            if len(cmds) == 0:
                command = name_fmt.format(name.title()) + command
            else:
                command = self._padding + command

            cmds.append(command)

        return cmds

    def general_help(self):
        name_fmt = self._row_format()

        commands = [
            'I am the Monitor of Installation 04. I am 343 Guilty Spark '
            'Try !help [command] if you need specific help any command',
            '\nThe commands available are:\n',
            name_fmt.format('Plugin') + 'Command\n',
            '-' * int(self._longest * 2.5)
        ]
        for name, plugin in self._plugins:
            if not plugin.commands:
                continue

            commands += self._plugin_cmds(name, plugin, name_fmt)

        return '\n'.join(commands)

    async def command_help(self, command):
        if not command.startswith(self.bot.prefix):
            command = self.bot.prefix + command

        if command in self.bot.commands:
            await self.bot.commands[command].help(command)
        else:
            await self.bot.say(
                'I\'m not familiar with that command, curious')

    async def on_command(self, _, message: discord.Message):
        """ Prints the relevant help information

        :param message:
            The message to respond to
        """
        args = message.content.split()
        if len(args) == 1 or len(args) > 2:
            await self.bot.code(self.general_help(), language='css')
        else:
            await self.command_help(args[1])
