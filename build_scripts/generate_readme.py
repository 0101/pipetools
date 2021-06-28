"""
A script for generating a README file from docs/overview page
"""

import codecs
import re

from pipetools import foreach, X, pipe


DOC_ROOT = 'https://0101.github.io/pipetools/doc/'


readme_template = """
Pipetools
=========

|tests-badge| |coverage-badge| |pypi-badge|

.. |tests-badge| image:: https://github.com/0101/pipetools/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/0101/pipetools/actions/workflows/tests.yml

.. |coverage-badge| image:: build_scripts/coverage.svg
  :target: https://github.com/0101/pipetools/actions/workflows/tests.yml

.. |pypi-badge| image:: https://img.shields.io/pypi/dm/pipetools.svg
  :target: https://pypi.org/project/pipetools/

`Complete documentation <{0}>`_

{{0}}

But wait, there is more
-----------------------
Checkout `the Maybe pipe <{0}maybe>`_, `partial application on steroids <{0}xpartial>`_
or `automatic data structure creation <{0}pipeutils#automatic-data-structure-creation>`_

See the `full documentation <{0}#contents>`_.
""".format(DOC_ROOT)


link_template = u"`{text} <%s{url}>`_" % DOC_ROOT


link_replacements = (
    # :doc:`pipe-utils' documentation<pipeutils>`.
    (r":doc:`([^<]*)<([^>]*)>`", {'url': r'\2.html', 'text': r'\1'}),

    # :func:`~pipetools.utils.where`
    (r":func:`~pipetools\.utils\.([^`]*)`",
        {'url': r'pipeutils.html#pipetools.utils.\1', 'text': r'\1()'}),

) > foreach([X[0] | re.compile, X[1] | link_template])


def create_readme():
    with codecs.open('docs/source/overview.rst', 'r', 'utf-8') as overview:
        with codecs.open('README.rst', 'w+', 'utf-8') as readme:
            overview.read() > pipe | fix_links | readme_template | readme.write


def fix_links(string):
    for pattern, replacement in link_replacements:
        string = pattern.sub(replacement, string)
    return string


if __name__ == '__main__':

    create_readme()
