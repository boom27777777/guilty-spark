import asyncio
import yaml
from guilty_spark.application import bot

usage = 'Usage: !bindmeme [in/is]::[trigger]::[meme]'

with open('shitpost.yml') as memes:
    dreams = yaml.load(memes)


def cache_memes():
    with open('shitpost.yml', 'w') as memes:
        yaml.dump(dreams, memes, default_flow_style=False)


@asyncio.coroutine
def on_message(message):
    global dreams
    if '!bindmeme' in message.content:
        content = message.content.replace('!bindmeme', '')
        args = content.split('::')
        if len(args) != 3:
            yield from bot.say(usage)
            return
        meme_type, trigger, meme = [a.strip() for a in args]
        if meme_type not in ['in', 'is']:
            yield from bot.say(usage)
            return
        if len(trigger) < 3:
            yield from bot.say('Trigger needs to be more then 3 characters')
            return

        dreams['memes'][meme_type][trigger] = meme
        cache_memes()
        yield from bot.say('Meme bound')
        return

    memes = dreams['memes']
    if message.content in memes['is']:
        yield from bot.say(memes['is'][message.content])
        return

    for meme in memes['in']:
        if meme in message.content:
            yield from bot.say(memes['in'][meme])
            return
