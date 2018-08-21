"""
:Date: 2016-08-01
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import json
from random import randint
from urllib.parse import urlencode

from guilty_spark.networking import get
from guilty_spark.plugin_system.dynamic import Dynamic

usage = 'Usage: !gif [search]'

dyn = Dynamic()


@dyn.command(glob=True)
async def gif(*search):
    """Grabs a random gif for a given search term"""

    url = 'http://api.giphy.com/v1/gifs/search?' + \
          urlencode([('q', '+'.join(search))]) + \
          '&api_key=dc6zaTOxFJmzC'

    blob = await get(url)
    data = json.loads(blob)
    gifs = data['data']

    if len(gifs) > 0:
        gif_id = randint(0, len(gifs) - 1)
        gif_url = gifs[gif_id]['images']['downsized_medium']['url']
        return gif_url
    else:
        return {
            'title': 'Disappointment',
            'description': 'No gifs found, today is a sad day.',
            'level': 2
        }
