"""
:Date: 2018-08-19
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)

Goal
----
    A simple RSS parsing library. Not good for much more then RSS.
"""

import html
import re


def get_tags(raw, needle, strip_tag=True):
    """ Naive XML Parser that builds a list of **needle** tags, and returns the contents

    :param raw: The XML to parse
    :param needle: The Tag to build a list from I.E. <item></item>
    :return: List of the contents of every occurrence of needle
    """

    tags = []
    tag = ''
    body = ''
    in_tag = False
    in_body = False
    in_cdata = False

    for ch in raw:
        if 'CDATA' in body:
            in_cdata = True

        if in_cdata and ']]' in body:
            in_cdata = False

        if ch == '<' and not in_cdata:
            in_tag = True
            tag = ''

        if not in_tag and not in_body:
            continue

        if in_body:
            body += ch

        if in_tag and not in_cdata:
            tag += ch
            if ch in ' >':
                in_tag = False

                if tag.strip('< >') == needle:
                    in_body = True
                    body = ''

                if tag.strip('< >') == '/' + needle:
                    in_body = False
                    if strip_tag:
                        tags.append(body.replace(tag, '').strip())
                    else:
                        tags.append(tag.strip() + body.strip())

    return tags


def format(raw_tag):
    tag = raw_tag
    if 'CDATA' in raw_tag:
        # Strip CDATA tag
        tag = re.sub('<!.*\[CDATA\[', ' ', tag)
        tag = re.sub(']]>', ' ', tag)

        # Strip extra HTML
        tag = re.sub('<([A-Za-z\/]+)>|<(a[^>]*)>', ' ', tag)
        # Strip extra Whitespace
        tag = re.sub(' +', ' ', tag)

    tag = html.unescape(tag)

    return tag


def unwrap(lst):
    try:
        return format(str(lst[0]))
    except IndexError:
        return ''


def get_image(raw_item):
    image = ''

    possible_images = [
        '<media:content.*url=\"([^\"]*)\"',
        '<img[^>]*src="([^\"]+)"'
    ]

    for location in possible_images:
        try:
            image = re.search(location, raw_item).group(1)
        except AttributeError:
            continue

        if image:
            break

    return image


def parse_item(raw_item):
    return {
        'title': unwrap(get_tags(raw_item, 'title')),
        'link': unwrap(get_tags(raw_item, 'link')),
        'description': unwrap(get_tags(raw_item, 'description')),
        'date': unwrap(get_tags(raw_item, 'pubDate')),
        'image': get_image(html.unescape(raw_item))
    }


def get_items(raw_feed):
    items = []

    for item in get_tags(raw_feed, 'item'):
        items.append(parse_item(item))

    return items


def get_title(raw_feed):
    return unwrap(get_tags(raw_feed, 'title'))
