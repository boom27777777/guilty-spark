"""
:Date: 2016-08-13
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----


Usage
-----
    ``$ python dynamic``
"""
import asyncio
import discord
from guilty_spark.plugin_system.plugin import Plugin


class Dynamic:
    def __init__(self):
        self.commands = {}

    def command(self, glob=False, context=False):
        def _wrap(func):
            cmd = func.__name__
            if not glob:
                args = list(
                    func.__code__.co_varnames[:func.__code__.co_argcount]
                )
            else:
                args = [func.__code__.co_varnames[0]]

            if context:
                args.pop(0)

            usage = 'Usage: {{}}{} {}'.format(
                cmd, ' '.join('[{}]'.format(v) for v in args))
            help = (func.__doc__ or '') + '\n' + usage

            self.commands[cmd] = (args, usage, help, func, glob, context)

        return _wrap

    def _make_plugin(self, cmds):
        class plug(Plugin):
            def __init__(self, name, bot):
                super().__init__(name, bot, commands=cmds.keys())

            def _strip_prefix(self, command):
                return command.replace(self.bot.prefix, '')

            def _prefix(self, string):
                return string.format(self.bot.prefix)

            @asyncio.coroutine
            def help(self, command):
                command = self._strip_prefix(command)
                _, help = cmds[command]
                yield from self.bot.code(self._prefix(help))

            @asyncio.coroutine
            def on_command(self, command: str, message: discord.Message):
                command = self._strip_prefix(command)
                func, *_ = cmds[command]
                try:
                    yield from self.bot.say(func(message))
                except IndexError as e:
                    yield from self.bot.code(self._prefix(str(e)))

        return plug

    def make_plug(self):
        cmds = {}
        for cmd, vals in self.commands.items():
            params, usage, help, func, glob, message = vals

            def _func(msg):
                _, *args = msg.content.rstrip().split()
                is_globed = glob and len(args) > 0

                if message:
                    return func(msg)

                elif len(args) == len(params) or is_globed:
                    return func(*args)

                else:
                    raise IndexError(usage)

            cmds[cmd] = (_func, help)
        return self._make_plugin(cmds)
