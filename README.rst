
Pipetools
=========

|tests-badge| |coverage-badge| |pypi-badge|

.. |tests-badge| image:: https://github.com/0101/pipetools/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/0101/pipetools/actions/workflows/tests.yml

.. |coverage-badge| image:: https://raw.githubusercontent.com/0101/pipetools/master/coverage.svg
  :target: https://github.com/0101/pipetools/actions/workflows/tests.yml

.. |pypi-badge| image:: https://img.shields.io/pypi/dm/pipetools.svg
  :target: https://pypi.org/project/pipetools/

`Complete documentation <https://0101.github.io/pipetools/doc/>`_

``pipetools`` enables function composition similar to using Unix pipes.

It allows forward-composition and piping of arbitrary functions - no need to decorate them or do anything extra.

It also packs a bunch of utils that make common operations more convenient and readable.

Source is on github_.

.. _github: https://github.com/0101/pipetools

Why?
----

Piping and function composition are some of the most natural operations there are for
plenty of programming tasks. Yet Python doesn't have a built-in way of performing them.
That forces you to either deep nesting of function calls or adding extra **glue code**.


Example
-------

Say you want to create a list of python files in a given directory, ordered by
filename length, as a string, each file on one line and also with line numbers:

.. code-block:: pycon

    >>> print(pyfiles_by_length('../pipetools'))
    1. ds_builder.py
    2. __init__.py
    3. compat.py
    4. utils.py
    5. main.py

All the ingredients are already there, you just have to glue them together. You might write it like this:

.. code-block:: python

    def pyfiles_by_length(directory):
        all_files = os.listdir(directory)
        py_files = [f for f in all_files if f.endswith('.py')]
        sorted_files = sorted(py_files, key=len, reverse=True)
        numbered = enumerate(py_files, 1)
        rows = ("{0}. {1}".format(i, f) for i, f in numbered)
        return '\n'.join(rows)

Or perhaps like this:

.. code-block:: python

    def pyfiles_by_length(directory):
        return '\n'.join('{0}. {1}'.format(*x) for x in enumerate(reversed(sorted(
            [f for f in os.listdir(directory) if f.endswith('.py')], key=len)), 1))

Or, if you're a mad scientist, you would probably do it like this:

.. code-block:: python

    pyfiles_by_length = lambda d: (reduce('{0}\n{1}'.format,
        map(lambda x: '%d. %s' % x, enumerate(reversed(sorted(
            filter(lambda f: f.endswith('.py'), os.listdir(d)), key=len))))))


But *there should be one -- and preferably only one -- obvious way to do it*.

So which one is it? Well, to redeem the situation, ``pipetools`` give you yet
another possibility!

.. code-block:: python

    pyfiles_by_length = (pipe
        | os.listdir
        | where(X.endswith('.py'))
        | sort_by(len).descending
        | (enumerate, X, 1)
        | foreach("{0}. {1}")
        | '\n'.join)

*Why would I do that*, you ask? Comparing to the *native* Python code, it's

- **Easier to read** -- minimal extra clutter
- **Easier to understand** -- one-way data flow from one step to the next, nothing else to keep track of
- **Easier to change** -- want more processing? just add a step to the pipeline
- **Removes some bug opportunities** -- did you spot the bug in the first example?

Of course it won't solve all your problems, but a great deal of code *can*
be expressed as a pipeline, giving you the above benefits. Read on to see how it works!


Installation
------------

.. code-block:: console

    $ pip install pipetools

`Uh, what's that? <https://pip.pypa.io>`_


Usage
-----

.. _the-pipe:

The pipe
""""""""
The ``pipe`` object can be used to pipe functions together to
form new functions, and it works like this:

.. code-block:: python

    from pipetools import pipe

    f = pipe | a | b | c

    # is the same as:
    def f(x):
        return c(b(a(x)))


A real example, sum of odd numbers from 0 to *x*:

.. code-block:: python

    from functools import partial
    from pipetools import pipe

    odd_sum = pipe | range | partial(filter, lambda x: x % 2) | sum

    odd_sum(10)  # -> 25


Note that the chain up to the `sum` is lazy.


Automatic partial application in the pipe
"""""""""""""""""""""""""""""""""""""""""

As partial application is often useful when piping things together, it is done
automatically when the *pipe* encounters a tuple, so this produces the same
result as the previous example:

.. code-block:: python

    odd_sum = pipe | range | (filter, lambda x: x % 2) | sum

    # Automatic partial with *args
    range_args: tuple[int, int, int] = (1, 20, 2)
    # Using pipe
    my_range: Callable = pipe | range | range_args
    # Using tuple
    my_range: Callable = pipe | (range, range_args)
    # list(my_range()) == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    # Automatic partial with **kwargs
    dataclass_kwargs: dict[str, bool] = {'frozen': True, 'kw_only': True, 'slots': True}
    # Using pipe
    my_dataclass: Callable = pipe | dataclass | dataclass_kwargs
    # Using tuple
    my_dataclass: Callable = pipe | (dataclass, dataclass_kwargs)
    @my_dataclass
    class Bla:
        foo: int
        bar: str

    # Bla(5, 'bbb') -> Raises TypeError: takes 1 positional argument but 3 were given
    # Bla(foo=5, bar='bbb').foo == 5

As of ``0.1.9``, this is even more powerful, see `X-partial  <https://0101.github.io/pipetools/doc/xpartial.html>`_.


Built-in tools
""""""""""""""

Pipetools contain a set of *pipe-utils* that solve some common tasks. For
example there is a shortcut for the filter class from our example, called
`where() <https://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.where>`_:

.. code-block:: python

    from pipetools import pipe, where

    odd_sum = pipe | range | where(lambda x: x % 2) | sum

Well that might be a bit more readable, but not really a huge improvement, but
wait!

If a *pipe-util* is used as first or second item in the pipe (which happens
quite often) the ``pipe`` at the beginning can be omitted:

.. code-block:: python

    odd_sum = range | where(lambda x: x % 2) | sum


See `pipe-utils' documentation <https://0101.github.io/pipetools/doc/pipeutils.html>`_.


OK, but what about the ugly lambda?
"""""""""""""""""""""""""""""""""""

`where() <https://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.where>`_, but also `foreach() <https://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.foreach>`_,
`sort_by() <https://0101.github.io/pipetools/doc/pipeutils.html#pipetools.utils.sort_by>`_ and other `pipe-utils <https://0101.github.io/pipetools/doc/pipeutils.html>`_ can be
quite useful, but require a function as an argument, which can either be a named
function -- which is OK if it does something complicated -- but often it's
something simple, so it's appropriate to use a ``lambda``. Except Python's
lambdas are quite verbose for simple tasks and the code gets cluttered...

**X object** to the rescue!

.. code-block:: python

    from pipetools import where, X

    odd_sum = range | where(X % 2) | sum


How 'bout that.

`Read more about the X object and it's limitations. <https://0101.github.io/pipetools/doc/xobject.html>`_


.. _auto-string-formatting:

Automatic string formatting
"""""""""""""""""""""""""""

Since it doesn't make sense to compose functions with strings, when a pipe (or a
`pipe-util <https://0101.github.io/pipetools/doc/pipeutils.html>`_) encounters a string, it attempts to use it for
`(advanced) formatting`_:

.. code-block:: pycon

    >>> countdown = pipe | (range, 1) | reversed | foreach('{}...') | ' '.join | '{} boom'
    >>> countdown(5)
    '4... 3... 2... 1... boom'

.. _(advanced) formatting: http://docs.python.org/library/string.html#formatstrings


Feeding the pipe
""""""""""""""""

Sometimes it's useful to create a one-off pipe and immediately run some input
through it. And since this is somewhat awkward (and not very readable,
especially when the pipe spans multiple lines):

.. code-block:: python

    result = (pipe | foo | bar | boo)(some_input)

It can also be done using the ``>`` operator:

.. code-block:: python

    result = some_input > pipe | foo | bar | boo

    result = range(10) > pipe | sum # result==45

.. note::
    Note that the above method of input won't work if the input object
    defines `__gt__ <https://docs.python.org/3/reference/datamodel.html#object.__gt__>`_
    for *any* object - including the pipe. This can be the case for example with
    some objects from math libraries such as NumPy. If you experience strange
    results try falling back to the standard way of passing input into a pipe.


But wait, there is more
-----------------------
Checkout `the Maybe pipe <https://0101.github.io/pipetools/doc/maybe>`_, `partial application on steroids <https://0101.github.io/pipetools/doc/xpartial>`_
or `automatic data structure creation <https://0101.github.io/pipetools/doc/pipeutils#automatic-data-structure-creation>`_
in the `full documentation <https://0101.github.io/pipetools/doc/#contents>`_.
