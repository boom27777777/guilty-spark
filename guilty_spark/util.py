"""
:Date: 2016-08-03
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""


def cap_message(msg, front, back):
    """ Adds a string to the beginning and end of a message

    :param msg:
        The string to cap
    :param front:
        The front cap
    :param back:
        The back cap
    :return:
        The capped string
    """

    if front and not msg.startswith(front):
        msg = front + msg

    if back and not msg.endswith(back):
        msg += back

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

    front, back = None, None

    if isinstance(ends, list):
        limit -= len(''.join(ends))
        front, back = ends[0], ends[1]

    elif ends:
        limit -= len(ends) * 2
        front, back = ends, ends

    raw_parts = [msg[i:i + limit] for i in range(0, len(msg), limit)]
    parts = [cap_message(p, front=front, back=back) for p in raw_parts]

    return parts
