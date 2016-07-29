import logging
import urllib.request as requests


def fetch_page(url):
    """ Builds a request as the bot to request anything through HTTP

    :param url:
        The url to fetch
    :return:
        Response content or None if an error occurs
    """
    content = None
    try:
        request = requests.Request(url)
        opener = requests.build_opener()
        request.add_header(
            'User-Agent', 'GuiltySpark/1.0 (/u/CheetElwin)')
        content = opener.open(request).read()
    except requests.HTTPError:
        logging.error('Failed to fetch page %s', url)
    return content
