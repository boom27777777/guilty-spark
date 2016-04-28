import logging
import urllib.request as requests

def fetch_page(url):
    html = None
    try:
        request = requests.Request(url)
        opener = requests.build_opener()
        request.add_header(
            'User-Agent', 'GuiltySpark/1.0 (/u/CheetElwin)')
        html = opener.open(request).read()
    except requests.HTTPError:
        logging.error('Failed to fetch page %s', url)
    return html
