from discord import Message
from guilty_spark.bot import Monitor


class BasePlugin:
    def __init__(self, bot: Monitor):
        self.bot = bot

    def on_message(self, message: Message):
        pass

    def on_command(self, message: Message):
        pass

    def help(self):
        pass
