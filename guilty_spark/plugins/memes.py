import asyncio
import yaml
import re
from guilty_spark.application import bot

usage = 'Usage:\n' \
        '\t!bindmeme [in/is]::[trigger]::[meme]\n' \
        '\t!unbindmeme [trigger]'

try:
    with open('shitpost.yml') as memes:
        dreams = yaml.load(memes)
except IOError:
    dreams = {
        'memes':
            {
                'in': {},
                'is': {},
                're': {}
            }
    }

def cache_memes():
    with open('shitpost.yml', 'w') as memes:
        yaml.dump(dreams, memes, default_flow_style=False)


def delete_meme(trigger: str):
    for key in dreams['memes']:
        if trigger in dreams['memes'][key]:
            del dreams['memes'][key][trigger]
            cache_memes()
            return True
    return False


@asyncio.coroutine
def on_message(message):
    global dreams
    if message.content == '!help !bindmeme':
        yield from bot.say(
            ('Retune the dank emitters to include new autism\n\n{}\n\n'
             'in: trigger is anywhere in the message\n'
             'is: is exactly equal to trigger\n'
             're: RegEx matching\n'
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
        if meme_type not in ['in', 'is', 're']:
            yield from bot.say(usage)
            return
        if len(trigger) < 3:
            yield from bot.say('Trigger needs to be more then 3 characters')
            return

        try:
            dreams['memes'][meme_type][trigger] = meme
        except KeyError:
            dreams['memes'][meme_type] = {}
            dreams['memes'][meme_type][trigger] = meme

        cache_memes()
        yield from bot.say('Meme bound')
        return

    if '!unbindmeme' in message.content:
        content = message.content.replace('!unbindmeme', '')
        arg = content.strip()

        if delete_meme(arg):
            yield from bot.say('Meme unbound')
        else:
            yield from bot.say('You have given me stale memes')
        return

    memes = dreams['memes']
    if message.content in memes['is']:
        yield from bot.say(memes['is'][message.content])
        return

    for meme, autism in memes['in'].items():
        if meme in message.content:
            yield from bot.say(autism)
            return

    for meme, autism in memes['re'].items():
        if re.search(meme, message.content):
            yield from bot.say(autism)
            return
