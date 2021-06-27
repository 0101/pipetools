"""
A script for generating a README file and publishing docs on github pages.
"""

import codecs
import re
from paver.easy import sh, BuildFailure
from pipetools import foreach, foreach_do, where, X, pipe, unless


DOC_ROOT = 'http://0101.github.io/pipetools/doc/'


readme_template = """
`Complete documentation in full color <{0}>`_.

.. image:: https://github.com/0101/pipetools/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/0101/pipetools/actions/workflows/tests.yml

.. image:: coverage.svg

Pipetools
=========

{{0}}

But wait, there is more
-----------------------
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


commit_readme = """

git add README.rst
git commit -m "(readme update)"

"""


update_gh_pages = """

git checkout gh-pages
git merge master

git rm -rf doc
sphinx-build -b html docs/source/ doc

git add doc
git commit -m "doc update"
git checkout master

"""

runscript = X.split('\n') | where(X) | unless(BuildFailure, foreach_do(sh))


if __name__ == '__main__':

    create_readme()
    runscript(commit_readme)
    runscript(update_gh_pages)
