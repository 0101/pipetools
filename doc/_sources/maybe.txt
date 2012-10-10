The Maybe Pipe
==============

``maybe`` is just like :ref:`pipe <the-pipe>`, except if any of the piped functions
returns ``None`` the execution is stopped and ``None`` is returned immediately.

Example::

    >>> from pipetools import maybe, X
    >>> f = maybe | (re.match, r'^number-(\d+)$') | X.group(1) | int
    >>> f('number-7')
    7
    >>> f('something else')
    None


Can be used together with :func:`~pipetools.utils.unless` to great effect::

    content = 'file.txt' > maybe | unless(IOError, open) | X.read()
