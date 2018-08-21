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
from guilty_spark.networking import get

from .simple_rss import get_items, get_title


class RSS(Plugin):

    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['rss'])
        self.feeds = CachedDict('rss-feeds')

    async def help(self, command: str):
        embed = self.build_embed(
            title='RSS Feeds',
            description='Tracks RSS feeds, and gives you updates\n\n'
                        '**Usage**: `{}rss [subcommand]`\n\n'
                        '**Subcommands**:'.format(self.bot.prefix)
        )

        embed.add_field(
            name='`subscribe [Feed Link]`',
            value='Adds a new feed to this channel',
            inline=False
        )

        embed.add_field(
            name='`unsubscribe [Feed Link]`',
            value='Removes a feed from this channel',
            inline=False
        )

        embed.add_field(
            name='`list`',
            value='Lists registered feeds',
            inline=False
        )
        await self.bot.send_embed(embed)

    async def on_ready(self):
        await self.feeds.load()

        while True:
            await self.update_feeds()
            await asyncio.sleep(60 * 60)  # Poll feeds every hour

    def build_message(self, post):
        embed = self.build_embed(
            title=post['title'],
            description=post['date'],
            fields={
                post['link']: post['description']
            }
        )
        if post['image']:
            embed.set_image(url=post['image'])

        return embed

    async def post_feed(self, channels, post):
        message = self.build_message(post)
        for channel in channels:
            await self.bot.send_embed(message, channel=channel)

    async def update_feed(self, items, feed):
        new_posts = []
        for new in items:
            if new['link'] == feed['last'] or len(new_posts) >= 5:
                break

            new_posts.append(new)

        for post in new_posts[::-1]:
            await self.post_feed(feed['channels'], post)

        feed['last'] = new_posts[0]['link']
        await self.feeds.cache()

    async def do_update(self, link, feed):
        try:
            raw_feed = await get(link)
        except:  # Need to come up with a better Error Strategy
            raise

        items = get_items(raw_feed)

        if feed.setdefault('title', 'N/A') == 'N/A':
            feed['title'] = get_title(raw_feed)
            await self.feeds.cache()

        if not feed['last']:
            feed['link'] = items[0]['link']
            await self.feeds.cache()

        if items and items[0]['link'] != feed['last']:
            await self.update_feed(items, feed)

    async def update_feeds(self):
        for link, feed in self.feeds.items():
            if link:
                await self.do_update(link, feed)

    async def register_feed(self, channel, feed):
        if feed not in self.feeds:
            self.feeds[feed] = {
                'title': 'N/A',
                'last': '',
                'channels': [channel.id]
            }

        else:
            if channel.id not in self.feeds[feed]['channels']:
                self.feeds[feed]['channels'].append(channel.id)

        await self.feeds.cache()
        await self.bot.send_embed(self.build_embed(
            title='Success',
            description='Feed registered'
        ))

    async def remove_feed(self, channel, feed):
        if feed in self.feeds:
            self.feeds[feed]['channels'].remove(channel.id)
            if not self.feeds[feed]['channels']:
                del self.feeds[feed]

            await self.feeds.cache()
            await self.bot.send_embed(self.build_embed(
                title='Success',
                description='Unsubscribed from feed <{}>'.format(feed)
            ))

        else:
            await self.bot.send_embed(self.build_embed(
                title='Error',
                description='Feed (<{}>) not subscribed on this channel'.format(feed),
                level=2
            ))

    async def list(self, channel):
        embed = self.build_embed(
            title='Registered RSS Feeds',
            description='Feeds registered for #{}'.format(
                self.bot.current_message.channel.name)
        )
        num_feeds = 0
        for link, feed in self.feeds.items():
            if channel.id in feed['channels']:
                num_feeds += 1
                embed.add_field(
                    name='{}. {}'.format(num_feeds, feed.setdefault('title', 'N/A')),
                    value=link,
                    inline=False
                )

        await self.bot.send_embed(embed)

    async def on_command(self, command, message: discord.Message):
        subcommand, *args = message.content.replace(command, '').split()

        if subcommand == 'subscribe':
            if len(args) != 1:
                await self.help(command)
                return

            await self.register_feed(message.channel, args[0])

        if subcommand == 'list':
            if len(args) != 1:
                await self.list(message.channel)
            else:
                await self.list(args[0])

        if subcommand == 'unsubscribe':
            if len(args) != 1:
                await self.help(command)

            await self.remove_feed(message.channel, args[0])

        if int(message.author.id) == self.bot.settings['owner'] and subcommand == 'force-update':
            await self.update_feeds()
            await self.bot.say('Feeds updated.')
