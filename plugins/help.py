import asyncio
import discord

from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import Plugin

usage = 'Usage: !help [command]'


class Help(Plugin):
    def __init__(self, name, bot: Monitor):
        super().__init__(name, bot, commands=['help'])

    @asyncio.coroutine
    def help(self):
        yield from self.bot.code('Gives you helps \n' + usage)

    @asyncio.coroutine
    def on_command(self, command, message: discord.Message):
        """ Prints the relevant help information

        :param message:
            The message to respond to
        """
        args = message.content.split()
        if len(args) == 1 or len(args) > 2:
            commands = '\n\nThe commands available are:\n\t'
            commands += '\n\t'.join(
                [c for c, p in self.bot.commands.items() if p.enabled]
            )
            yield from self.bot.code(self.bot.help_message + commands)
        else:
            command = args[1]

            if not command.startswith(self.bot.prefix):
                command = self.bot.prefix + command

            if command in self.bot.commands:
                yield from self.bot.commands[command].help()
            else:
                yield from self.bot.say("I'm not familiar with that command, curious")
