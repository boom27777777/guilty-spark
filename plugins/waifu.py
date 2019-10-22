"""
:Date: 2019-10-20
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import json
from io import BytesIO
from base64 import b64decode

from guilty_spark.networking import post
from guilty_spark.plugin_system.dynamic import Dynamic, DynamicError

usage = 'Usage: !waifu'

api_endpoint = 'https://api.waifulabs.com/generate'

dyn = Dynamic()


async def get_waifu():
    blob = await post(api_endpoint, json.dumps({'step': 0}))

    if not blob:
        raise DynamicError('Failed to fetch waifu')

    data = json.loads(blob)
    girl = data.get('newGirls')[0].get('image')

    return BytesIO(b64decode(girl))


@dyn.command()
async def waifu():
    """Generates a Waifu using the weeb AI at https://waifulabs.com"""

    image = await get_waifu()
    setattr(image, 'file_name', 'waifu.png')
    return image
