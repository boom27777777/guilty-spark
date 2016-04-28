import asyncio
import yaml
from guilty_spark.application import bot

usage = 'Usage:\n' \
        '\t!bindmeme [in/is]::[trigger]::[meme]\n' \
        '\t!unbindmeme [trigger]'

with open('shitpost.yml') as memes:
    dreams = yaml.load(memes)


def cache_memes():
    with open('shitpost.yml', 'w') as memes:
        yaml.dump(dreams, memes, default_flow_style=False)


@asyncio.coroutine
def on_message(message):
    if message.content == '!help !bindmeme':
        yield from bot.say(
            ('Retune the dank emitters to include new autism\n\n{}\n\n'
             'in: trigger is anywhere in the message\n'
             'is: is exactly equal to trigger\n'
             'Example:'
             '!bindmeme is::kthx::bai'
             ).format(usage))
        return

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

    if '!unbindmeme' in message.content:
        content = message.content.replace('!unbindmeme', '')
        arg = content.strip()

        if arg in dreams['memes']['in']:
            del dreams['memes']['in'][arg]
            yield from bot.say('Meme unbound')
            cache_memes()

        elif arg in dreams['memes']['is']:
            del dreams['memes']['is'][arg]
            yield from bot.say('Meme unbound')
            cache_memes()

        else:
            yield from bot.say('You have given me stale memes')
        return

    memes = dreams['memes']
    if message.content in memes['is']:
        yield from bot.say(memes['is'][message.content])
        return

    for meme in memes['in']:
        if meme in message.content:
            yield from bot.say(memes['in'][meme])
            return
