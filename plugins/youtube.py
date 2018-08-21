"""
:Date: 2016-08-14
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import re
from urllib.parse import urlencode

from guilty_spark.plugin_system.dynamic import Dynamic
from guilty_spark.networking import get

dyn = Dynamic()


@dyn.command(glob=True)
async def youtube(*search):
    """Grabs the first related youtube video for a given search"""

    parameters = urlencode([('search_query', '+'.join(search))])
    html = await get('https://www.youtube.com/results?' + parameters)
    links = re.findall('<a href="(/watch\?v=[^"]+)"', html)
    if links:
        link = 'http://youtube.com' + links[0]
        return link
    else:
        return 'No video found'
