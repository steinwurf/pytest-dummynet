import os
import io
import re
import sys

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8") as fd:
    long_description = fd.read()

with io.open(os.path.join(cwd, "wscript"), encoding="utf-8") as fd:

    VERSION = None

    regex = re.compile(
        r"""
    (                   # Group and match
        VERSION         #    Match 'VERSION'
        \s*             #    Match zero or more spaces
        =               #    Match and equal sign
        \s*             #    Match zero or more spaces
    )                   # End group
    "                   # Match "
    (                   # Group and match
         \d+\.\d+\.\d+  #    Match digit(s).digit(s).digit(s) e.g. 10.2.3
    )                   # End of group
    "                   # Match "
    """,
        re.VERBOSE,
    )

    for line in fd:

        match = regex.match(line)
        if not match:
            continue

        # The second parenthesized subgroup.
        VERSION = match.group(2)
        break

    else:
        sys.exit("No VERSION variable defined in wscript - aborting!")

setup(
    name="pytest-dummynet",
    version=VERSION,
    description=("A py.test plugin providing access to a dummynet."),
    long_description=long_description,
    url="https://github.com/steinwurf/pytest-dummynet",
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    license='BSD 3-clause "New" or "Revised" License',
    classifiers=[
        "Framework :: Pytest",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
    ],
    keywords=("pytest py.test " "testing unit tests plugin dummynet"),
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    install_requires=["pytest", "docker"],
    entry_points={
        "pytest11": ["dummynet = pytest_dummynet.fixtures"],
    },
)
