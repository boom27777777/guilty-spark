"""
:Date: 2016-08-03
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""


def cap_message(msg, ends=''):
    """ Adds a string to the beginning and end of a message

    :param msg:
        The string to cap
    :param ends:
        What to cap the string with
    :return:
        The capped string
    """

    if ends and not msg.startswith(ends):
        msg += ends

    elif ends and not msg.endswith(ends):
        msg = ends + msg

    return msg


def slice_message(limit, msg, ends=''):
    """ Slice a message into limit sized chunks adjusted to include the ends

    :param limit:
        Max size of string
    :param msg:
        The message to slice
    :param ends:
        The ends to cap a message with
    :return:
        A list of strings adjusted to
    """

    if ends:
        limit -= len(ends) * 2

    raw_parts = [msg[i:i + limit] for i in range(0, len(msg), limit)]
    parts = [cap_message(p, ends) for p in raw_parts]

    return parts
