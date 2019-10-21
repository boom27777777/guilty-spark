"""
:Date: 2016-08-13
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import asyncio
import discord
from collections import OrderedDict
from guilty_spark.plugin_system.plugin import Plugin


class DynamicError(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


class Dynamic:
    def __init__(self):
        self.commands = {}

    @staticmethod
    def _build_args(func, glob):
        code = func.__code__
        if not glob:
            args = code.co_varnames[:code.co_argcount]
        else:
            args = [code.co_varnames[0]]

        return list(args)

    @staticmethod
    def _build_usage(cmd, args):
        return '```Usage: {{}}{} {}```'.format(
            cmd, ' '.join('[{}]'.format(v) for v in args))

    def command(self, glob=False, context=False):
        def _wrap(func):
            cmd = func.__name__
            args = self._build_args(func, glob)

            if context:
                args.pop(0)

            usage = self._build_usage(cmd, args)

            vals = OrderedDict([
                ('args', args),
                ('usage', usage),
                ('help', (func.__doc__ or '') + '\n' + usage),
                ('func', func),
                ('flags', {
                    'glob': glob,
                    'context': context,
                }),
            ])
            self.commands[cmd] = vals

        return _wrap

    def _make_plugin(self, cmds):
        class Plug(Plugin):
            def __init__(self, name, bot):
                super().__init__(name, bot, commands=cmds.keys())

            def _strip_prefix(self, command):
                return command.replace(self.bot.prefix, '')

            def _prefix(self, string):
                return string.format(self.bot.prefix)

            async def help(self, command):
                command = self._strip_prefix(command)
                _, hlp = cmds[command]

                await self.bot.send_embed(
                    self.build_embed(
                        title=command.title(),
                        description=self._prefix(hlp)
                    )
                )

            async def on_command(self, command: str, message: discord.Message):
                command = self._strip_prefix(command)
                func, *_ = cmds[command]
                try:
                    result = await func(message)

                    if type(result) is str:
                        await self.bot.say(result)

                    elif type(result) is dict:
                        await self.bot.send_embed(self.build_embed(**result))

                    elif hasattr(result, 'read'):
                        name = 'file'

                        if hasattr(result, 'file_name'):
                            name = result.file_name

                        await self.bot.send_file(message.channel, result, filename=name)

                except DynamicError as e:
                    await self.bot.send_embed(
                        self.build_embed(
                            title="Error!",
                            description=self._prefix(str(e)),
                            level=2
                        )
                    )

        return Plug

    def make_plug(self):
        cmds = {}
        for cmd, vals in self.commands.items():
            params, usage, hlp, func, flags = vals.values()

            async def _func(msg):
                _, *args = msg.content.rstrip().split()
                is_globed = flags['glob'] and len(args) > 0

                if flags['context']:
                    return await func(msg)

                elif len(args) == len(params) or is_globed:
                    return await func(*args)

                else:
                    raise DynamicError(usage)

            cmds[cmd] = (_func, hlp)

        return self._make_plugin(cmds)
