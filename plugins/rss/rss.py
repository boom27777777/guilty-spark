"""
:Date: 2018-08-19
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----
    Provide an easy to use RSS feed subscription interface

"""
import asyncio
import discord

from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.plugin_system.data import CachedDict
from guilty_spark.networking import fetch_page

from .simple_rss import get_items


def get_posts(feed):
    return get_items(fetch_page(feed).decode())


class RSS(Plugin):

    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['rss'])
        self.feeds = CachedDict('rss-feeds')

    async def on_ready(self):
        await self.feeds.load()

        while True:
            await self.update_feeds()
            await asyncio.sleep(60 * 60)  # Poll feeds every hour
    
    def build_message(self, post):
        return self.build_embed(
            title=post['title'],
            fields={
                post['link']: post['description']
            }
        )
    
    async def post_feed(self, channels, post):
        message = self.build_message(post)
        for channel in channels:
            await self.bot.send_embed(message, channel=channel)

    async def update_feeds(self):
        for link, feed in self.feeds.items():
            if link:
                try:
                    recent_post = get_posts(link)[0]
                except:  # Need to come up with a better Error Strategy
                    raise

                if recent_post['link'] != feed['last']:
                    await self.post_feed(feed['channels'], recent_post)
                    feed['last'] = recent_post['link']
                    await self.feeds.cache()

    async def register_feed(self, chan_id, feed):
        if feed not in self.feeds:
            self.feeds[feed] = {
                'last': '',
                'channels': [chan_id]
            }

        else:
            if chan_id not in self.feeds['channels']:
                self.feeds[feed]['channels'].append(chan_id)

        await self.feeds.cache()

    async def list(self, chan_id):
        embed = self.build_embed(
            title='Registered RSS Feeds',
            description='\n'.join(self.feeds)
        )
        await self.bot.send_embed(embed)

    async def on_command(self, command, message: discord.Message):
        subcommand, *args = message.content.replace(command, '').split()
        
        if subcommand == 'register':
            if len(args) != 1:
                await self.help(command)
                return

            await self.register_feed(message.channel.id, args[0])
            await self.bot.say('Feed Registered')

        if subcommand == 'list':
            if len(args) != 1:
                await self.list(message.channel.id)
            else:
                await self.list(args[0])

        if message.author.id == self.bot.owner and subcommand == 'force-update':
            await self.update_feeds()
