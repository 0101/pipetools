from setuptools import setup
from setuptools.command.test import test as TestCommand
import pipetools


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


setup(
    name='pipetools',
    version=pipetools.__versionstr__,
    packages=['pipetools'],
    include_package_data=True,
    install_requires=(
         'setuptools>=0.6b1',
    ),
    tests_require=(
        'pytest',
    ),
    cmdclass={'test': PyTest},
)
