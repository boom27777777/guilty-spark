import asyncio
import discord

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !help [command]'


class Help(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['help'])

    @asyncio.coroutine
    def help(self, _):
        yield from self.bot.code('Gives you helps \n' + usage)

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        """ Prints the relevant help information

        :param message:
            The message to respond to
        """
        args = message.content.split()
        if len(args) == 1 or len(args) > 2:
            longest = max([len(p) for p in self.bot.plugins])
            name_fmt = '\n  {{:>{}}}: '.format(longest)
            padding = '\n' + ' ' * (longest + 4)
            plugins = sorted(self.bot.plugins.items(), key=lambda x: x[0])

            commands = '\n\nThe commands available are:\n\t'
            commands += name_fmt.format('Plugin') + 'Command\n'
            commands += '-' * int(longest * 2.5)
            for name, plugin in plugins:
                if not plugin.commands:
                    continue

                commands += name_fmt.format(name.title())
                commands += padding.join(
                    [self.bot.prefix + c for c in plugin.commands])

            yield from self.bot.code(self.bot.help_message + commands,
                                     language='css')
        else:
            command = args[1]

            if not command.startswith(self.bot.prefix):
                command = self.bot.prefix + command

            if command in self.bot.commands:
                yield from self.bot.commands[command].help(command)
            else:
                yield from self.bot.say("I'm not familiar with that command, curious")
