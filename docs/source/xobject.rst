The X object
============

The ``X`` object is a shortcut for writing simple, one-argument lambdas.

It's roughly equivalent to this: ``lambda x: x``

Example::

    ~X.some_attr.some_func(1, 2, 3).whatever
    # produces:
    lambda x: x.some_attr.some_func(1, 2, 3).whatever

    ~(X > 5)
    # produces:
    lambda x: x > 5


Any of the :ref:`supported operations <x-supported-operations>` performed on an
``X`` object yield another one that remembers what was done to it, so they
can be chained.

The ``~`` operator creates the actual function that can be called (without
creating just another ``X`` instance). However, this can be omitted within
*pipe* and :doc:`pipeutils` context where ``X`` is converted to a function
automatically::

    users > where(X.is_staff) | foreach(X.first_name) | X[:10]


But you can make use of ``X`` even outside *pipetools*, you just have to
remember to prefix it with ``~``

::

    my_list = list(users)
    my_list.sort(key=~X.last_login.date())



.. _x-supported-operations:

Currently supported operations
------------------------------

These are added as I need them. If you're missing something you can add it
yourself or create an issue on github_.

.. _github: https://github.com/0101/pipetools


* call (``__call__``)::

    X()
    X(some, agrs, some=kwargs)


* equals (``__eq__``)::

    X == something


* not equal (``__ne__``)::

    X != something


* attribute access (``__getattr__``)::

    X.attr


* item access, slicing (``__getitem__``)::

    X['key']
    X[0]
    X[:10]
    X[::-1]


* greater than (``__gt__``)::

    X > 3


* less than (``__lt__``)::

    X < 3


* modulo (``__mod__``)::

    X % 2


* negate (``__neg__``)::

    -X


* multiplication (``__mul__``)::

    X * 3


* addition (``__add__``)::

    X + 3
    X + " ...that's what she said!"


* is contained in (``_in_``)

  Unfortunately, ``X in container`` can't be done (because the magic method is
  called on the container) so theres a special method for that::

        X._in_(container)
