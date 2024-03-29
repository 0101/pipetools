pipe-utils
==========

Generic piping utilities.

Other functions can be piped to them, from both sides, without having to use the
``pipe`` object. The resulting function then also inherits this functionality.

Built-in
--------

Even though these are defined in the ``pipetools.utils`` module, they're
importable directly from ``pipetools`` for convenience.

All of these that take a function as an argument can automatically partially
apply the given function with positional and/or keyword arguments, for example::

    foreach(some_func, foo, bar=None)

Is the same as::

    foreach(partial(some_func, foo, bar=None))

(As of ``0.1.9`` this uses :doc:`xpartial`)


They also automatically convert the :doc:`X object<xobject>` to an actual
function.

List of built-in utils
----------------------

.. automodule:: pipetools.utils
    :members:


Make your own
-------------

You can make your own, but you generally shouldn't need to, since you can pipe
any functions you like.

But if you feel like there's a generally reusable *pipe-util* missing, feel
free to add it via a pull request on github_.

.. _github: https://github.com/0101/pipetools

How to do it? Just write the function and stick the
:func:`~pipetools.decorators.pipe_util` decorator on it.

And optionally also :func:`~pipetools.decorators.auto_string_formatter` (see
:ref:`auto-string-formatting`) or
:func:`~pipetools.decorators.data_structure_builder`
(see :ref:`auto-ds-creation`) if it makes sense.


.. _auto-ds-creation:

Automatic data-structure creation
---------------------------------

Some of the utils, most importantly :func:`foreach`, offer a shortcut for
creating basic python data structures - ``list``, ``tuple`` and ``dict``.

It works like this (the ``| list`` at the end is just so we can see the result,
otherwise it would just give us ``<iterable thing at 0xasdf123>``)::

    >>> range(5) > foreach({X: X * 2}) | list
    [{0: 0}, {1: 2}, {2: 4}, {3: 6}, {4: 8}]

    >>> range(5) > foreach([X, X * '★']) | list
    [[0, ''], [1, '★'], [2, '★★'], [3, '★★★'], [4, '★★★★']]

It can also be combined with string formatting::

    >>> names = [('John', 'Matrix'), ('Jack', 'Slater')]
    >>> names > foreach({'name': "{0} {1}", 'initials': '{0[0]}. {1[0]}.'}) | list
    [{'initials': 'J. M.', 'name': 'John Matrix'},
     {'initials': 'J. S.', 'name': 'Jack Slater'}]

.. _auto-regex:

Automatic regex conditions
--------------------------
If you use a string instead of a function as a condition in
:func:`~pipetools.utils.where`, :func:`~pipetools.utils.where_not`,
:func:`~pipetools.utils.select_first` or :func:`~pipetools.utils.take_until` the
string will be used as a regex to match the input against. This will, of course,
work only if the items of the input sequence are strings.

Essentially::

    where(r'^some\-regexp?$')

is equivalent to::

    where(re.match, r'^some\-regexp?$')

As of ``0.3.2`` this also filters out ``None`` values instead of throwing an
exception. Making it equivalent to::

    where(maybe | (re.match, r'^some\-regexp?$'))

If you want to easily add this functionality to your own functions, you can use
the :func:`~pipetools.decorators.regex_condition` decorator.
