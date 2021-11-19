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

.. _x-tilde
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

Most Python operators are supported now, but if you're still
missing something you can add it yourself or create an issue on github_.

.. _github: https://github.com/0101/pipetools


* attribute access (``__getattr__``)::

    X.attr
    getattr(X, 'something')


* comparisons: ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``::

    X == something
    X <= 3


* unary arithmetic operators (``+``, ``-``)::

    +X
    -X


* binary arithmetic operators (``+``, ``-``, ``*``, ``**``, ``@``, ``/``, ``//``, ``%``)::

    X - 3
    X + " ...that's what she said!"
    3 - X  # works in both directions


* bitwise operators (``<<``, ``>>``, ``&``, ``^``)::

    1 >> X
    X & 64



Current limitations
-------------------

* call (``__call__``) will only work if X is not in the arguments::

    # will work
    X.method()
    X(some, agrs, some=kwargs)

    # will not work
    obj.method(X)
    some_function(X, some=X)
    X.do(X)


* item access or slicing (``__getitem__``) will only work if X is not in the
  in the index key::

    # will work
    X['key']
    X[0]
    X[:10]
    X[::-1]

    # will not work
    foo[X]
    bar[X:]
    baz[::X]
    X[X.columns]


* is contained in / contains (``in``)

  Unfortunately, ``X in container`` can't be done (because the magic method is
  called on the container) so there's a special method for that::

        X._in_(container)

  The opposite form ``item in X`` has not been implemented either.


* special methods (``~``, ``|``)

  They have been given :ref:`special meanings <x-tilde>` in pipetools,
  so could no more be used as bitwise operations.


* logical operators (``and``, ``or``, ``not``) will not work;
  they are not exposed as magic methods in Python.


* await operator (``await X``) has not been implemented
