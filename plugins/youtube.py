"""
:Date: 2016-08-14
:Version: 0.0.1
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""

import re
from urllib.parse import urlencode

from guilty_spark.plugin_system.dynamic import Dynamic
from guilty_spark.networking import fetch_page

dyn = Dynamic()


@dyn.command(glob=True)
def youtube(*search):
    """Grabs the first related youtube video for a given search"""

    parameters = urlencode([('search_query', '+'.join(search))])
    html = fetch_page('https://www.youtube.com/results?' + parameters)
    links = re.findall('<a href="(/watch\?v=[^"]+)"', html.decode())
    if links:
        link = 'http://youtube.com' + links[0]
        return link
    else:
        return 'No video found'
