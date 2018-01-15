
`Complete documentation in full color <http://0101.github.io/pipetools/doc/>`_.

.. image:: https://travis-ci.org/0101/pipetools.svg?branch=master
  :target: https://travis-ci.org/0101/pipetools

Pipetools
=========

``pipetools`` is a python package that enables function composition similar to
using Unix pipes.

Inspired by Pipe_ and Околомонадное_ (whatever that means...)

.. _Pipe: http://dev-tricks.net/pipe-infix-syntax-for-python
.. _Околомонадное: http://honeyman.livejournal.com/122675.html?nojs=1


It allows piping of arbitrary functions and comes with a few handy shortcuts.


Source is on github_.


.. _github: https://github.com/0101/pipetools

Why?
----

Pipetools attempt to simplify function composition and make it more readable.

Why piping instead of regular composition?
""""""""""""""""""""""""""""""""""""""""""
I believe it to be easier to read, write and think about from left to right /
top to bottom in the order that it's actually executed, instead of reversed
order as it is with regular function composition (``(f • g)(x) == f(g(x))``).


Example
-------

Say you want to create a list of python files in a given directory, ordered by
filename length, as a string, each file on one line and also with line numbers::

    >>> print pyfiles_by_length('../pipetools')
    0. main.py
    1. utils.py
    2. __init__.py
    3. ds_builder.py


So you might write it like this::

    def pyfiles_by_length(directory):
        all_files = os.listdir(directory)
        py_files = [f for f in all_files if f.endswith('.py')]
        py_files.sort(key=len)
        numbered = enumerate(py_files)
        rows = ("{0}. {1}".format(i, f) for i, f in numbered)
        return '\n'.join(rows)

Or perhaps like this::

    def pyfiles_by_length(directory):
        return '\n'.join('{0}. {1}'.format(*x) for x in enumerate(sorted(
            [f for f in os.listdir(directory) if f.endswith('.py')], key=len)))

Or, if you're a mad scientist, you would probably do it like this::

    pyfiles_by_length = lambda d: (reduce('{0}\n{1}'.format,
        map(lambda x: '%d. %s' % x, enumerate(sorted(
            filter(lambda f: f.endswith('.py'), os.listdir(d)), key=len)))))


But *there should be one -- and preferably only one -- obvious way to do it*.

So which one is it? Well, to redeem the situation, ``pipetools`` give you yet
another possibility!

::

    pyfiles_by_length = (pipe
        | os.listdir
        | where(X.endswith('.py'))
        | sort_by(len)
        | enumerate
        | foreach("{0}. {1}")
        | '\n'.join
    )


So is this `The Right Way™`_? Probably not, but I think it's pretty cool, so you
should give it a try! Read on to see how it works.

.. _`The Right Way™`: http://www.python.org/dev/peps/pep-0020/


Installation
------------

::

    $ pip install pipetools

`Uh, what's that? <http://www.pip-installer.org>`_


Usage
-----

.. _the-pipe:

The pipe
""""""""
The ``pipe`` object can be used to pipe functions together to
form new functions, and it works like this::

    from pipetools import pipe

    f = pipe | a | b | c

    f(x) == c(b(a(x)))


A real example, sum of odd numbers from 0 to *x*::

    from functools import partial
    from pipetools import pipe

    odd_sum = pipe | range | partial(filter, lambda x: x % 2) | sum

    odd_sum(10)  # -> 25


Note that the chain up to the `sum` is lazy.


Automatic partial application in the pipe
"""""""""""""""""""""""""""""""""""""""""

As partial application is often useful when piping things together, it is done
automatically when the *pipe* encounters a tuple, so this produces the same
result as the previous example::

    odd_sum = pipe | range | (filter, lambda x: x % 2) | sum

As of ``0.1.9``, this is even more powerful, see `X-partial  <http://0101.github.io/pipetools/doc/xpartial.html>`_.


Built-in tools
""""""""""""""

Pipetools contain a set of *pipe-utils* that solve some common tasks. For
example there is a shortcut for the filter class from our example, called
`where() <http://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.where>`_::

    from pipetools import pipe, where

    odd_sum = pipe | range | where(lambda x: x % 2) | sum

Well that might be a bit more readable, but not really a huge improvement, but
wait!

If a *pipe-util* is used as first or second item in the pipe (which happens
quite often) the ``pipe`` at the beginning can be omitted::

    odd_sum = range | where(lambda x: x % 2) | sum


See `pipe-utils' documentation <http://0101.github.io/pipetools/doc/pipeutils.html>`_.


OK, but what about the ugly lambda?
"""""""""""""""""""""""""""""""""""

`where() <http://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.where>`_, but also `foreach() <http://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.foreach>`_,
`sort_by() <http://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.sort_by>`_ and other `pipe-utils <http://0101.github.io/pipetools/doc/pipeutils.html>`_ can be
quite useful, but require a function as an argument, which can either be a named
function -- which is OK if it does something complicated -- but often it's
something simple, so it's appropriate to use a ``lambda``. Except Python's
lambdas are quite verbose for simple tasks and the code gets cluttered...

**X object** to the rescue!

::

    from pipetools import where, X

    odd_sum = range | where(X % 2) | sum


How 'bout that.

`Read more about the X object and it's limitations. <http://0101.github.io/pipetools/doc/xobject.html>`_


.. _auto-string-formatting:

Automatic string formatting
"""""""""""""""""""""""""""

Since it doesn't make sense to compose functions with strings, when a pipe (or a
`pipe-util <http://0101.github.io/pipetools/doc/pipeutils.html>`_) encounters a string, it attempts to use it for
`(advanced) formatting`_::

    >>> countdown = pipe | (range, 1) | reversed | foreach('{0}...') | ' '.join | '{0} boom'
    >>> countdown(5)
    u'4... 3... 2... 1... boom'

.. _(advanced) formatting: http://docs.python.org/library/string.html#formatstrings


Feeding the pipe
""""""""""""""""

Sometimes it's useful to create a one-off pipe and immediately run some input
through it. And since this is somewhat awkward (and not very readable,
especially when the pipe spans multiple lines)::

    result = (pipe | foo | bar | boo)(some_input)

It can also be done using the ``>`` operator::

    result = some_input > pipe | foo | bar | boo

.. note::
    Note that the above method of input won't work if the input object
    defines `__gt__ <https://docs.python.org/3/reference/datamodel.html#object.__gt__>`_
    for *any* object - including the pipe. This can be the case for example with
    some objects from math libraries such as NumPy. If you experience strange
    results try falling back to the standard way of passing input into a pipe.



But wait, there is more
-----------------------
See the `full documentation <http://0101.github.io/pipetools/doc/#contents>`_.
