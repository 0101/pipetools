import io
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

from pipetools import xpartial, X
import pipetools


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        error_code = pytest.main(self.test_args)
        sys.exit(error_code)


setup(
    name='pipetools',
    version=pipetools.__versionstr__,
    description=('A library that enables function composition similar to '
        'using Unix pipes.'),
    long_description='README.rst' > xpartial(io.open, X, encoding="utf-8") | X.read(),
    author='Petr Pokorny',
    author_email='petr@innit.cz',
    license='MIT',
    url='https://0101.github.io/pipetools/',
    packages=['pipetools'],
    include_package_data=True,
    install_requires=(
         'setuptools>=0.6b1',
    ),
    tests_require=(
        'pytest',
    ),
    cmdclass={'test': PyTest},

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
