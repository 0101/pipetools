import sys

if sys.version < '3':
    from itertools import imap as map
    from itertools import ifilter as filter
    range = xrange  # noqa
    text_type = unicode  # noqa
    string_types = basestring  # noqa
    dict_items = lambda d: d.iteritems()
else:
    from builtins import map, filter, range
    text_type = str
    string_types = str
    dict_items = lambda d: d.items()
