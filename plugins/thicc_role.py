import discord
import re

from guilty_spark.plugin_system.plugin import Plugin


class THICCRole(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['thicc'])

        self.use_whitelist = True

    async def help(self, command, message):
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
            await self.help(command, None)
            return

        name = 'THICC#{}'.format(args[0])
        user = re.findall('\d+', args[1])[0]

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
