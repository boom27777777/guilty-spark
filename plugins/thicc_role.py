import discord
import re

from guilty_spark.plugin_system.plugin import Plugin


class THICCRole(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['thicc'])

        self.use_whitelist = True

    async def help(self, _):
        embed = self.build_embed(
            title='THICC Group management',
            description='Auto \n\n'
                        '**Usage**: `{}thicc [group_name] [@user]`\n\n'.format(
                self.bot.prefix)
        )
        await self.bot.send_embed(embed)

    @Plugin.admin
    async def on_command(self, command, message: discord.Message):
        try:
            _, *args = message.content.split()
            if len(args) < 2:
                raise IndexError
        except IndexError:
            await self.help(command)
            return

        name = 'THICC#{}'.format(args[0])
        user = re.search('[0-9]+', args[1]).group(1)

        try:
            role = await self.bot.create_role(
                server=message.server,
                name=name,
                mentionable=True
            )
        except discord.Forbidden:
            await self.bot.send_embed(self.build_embed(
                title='Error',
                description='I do not have permissions to make new roles',
                level=2
            ))
            return

        try:
            await self.bot.add_roles(
                self.bot.get_user_by_id(user),
                role
            )
        except discord.Forbidden:
            await self.bot.send_embed(self.build_embed(
                title='Error',
                description='I do not have permissions to add roles to user',
                level=2
            ))
            return

        await self.bot.send_embed(self.build_embed(
            title="Success",
            description="Role {} Created and assinged to <@{}>".format(
                name,
                user
            )
        ))
