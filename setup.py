#!/usr/bin/env python
# setup
# Setup script for installing rumi
#
# Author:   Tianshu Li
# Created:  Nov.19 2021

"""
Setup script for installing rumi
"""

##########################################################################
## Imports
##########################################################################


import os
import codecs

from setuptools import setup
from setuptools import find_packages


##########################################################################
## Package Information
##########################################################################


## Basic information
with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

NAME = "rumi-i18n"
DESCRIPTION = "A static site translation monitoring tool"
AUTHOR = "Tianshu Li"
EMAIL = "tianshu@rotational.io"
LICENSE = "Apache"
REPOSITORY = "https://github.com/rotationalio/rumi"
PACKAGE = "rumi"

## Define the keywords
KEYWORDS = ["rumi", "python", "translation monitoring", "l10n"]

## Define the classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
]

## Important Paths
PROJECT = os.path.abspath(os.path.dirname(__file__))
REQUIRE_PATH = os.path.join("requirements", "requirements.txt")
VERSION_PATH = os.path.join(PACKAGE, "version.py")

## Directories to ignore in find_packages
EXCLUDES = (
    "tests",
    "bin",
    "docs",
    "fixtures",
    "register",
    "notebooks",
)


##########################################################################
## Helper Functions
##########################################################################


def read(*parts):
    """
    Assume UTF-8 encoding and return the contents of the file located at the
    absolute path from the REPOSITORY joined with *parts.
    """
    with codecs.open(os.path.join(PROJECT, *parts), "rb", "utf-8") as f:
        return f.read()


def get_version(path=VERSION_PATH):
    """
    Reads the version.py defined in the VERSION_PATH to find the get_version
    function, and executes it to ensure that it is loaded correctly.
    """
    namespace = {}
    exec(read(path), namespace)
    return namespace["get_version"]()


def get_requires(path=REQUIRE_PATH):
    """
    Yields a generator of requirements as defined by the REQUIRE_PATH which
    should point to a requirements.txt output by `pip freeze`.
    """
    for line in read(path).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


##########################################################################
## Define the configuration
##########################################################################


config = {
    "name": NAME,
    "version": get_version(),
    "description": DESCRIPTION,
    "long_description": LONG_DESCRIPTION,
    "long_description_content_type": "text/markdown",
    "license": LICENSE,
    "author": AUTHOR,
    "author_email": EMAIL,
    "maintainer": AUTHOR,
    "maintainer_email": EMAIL,
    "url": REPOSITORY,
    "download_url": "{}/tarball/v{}".format(REPOSITORY, get_version()),
    "packages": find_packages(where=PROJECT, exclude=EXCLUDES),
    "install_requires": list(get_requires()),
    "classifiers": CLASSIFIERS,
    "keywords": KEYWORDS,
    "zip_safe": False,
}


##########################################################################
## Run setup script
##########################################################################


if __name__ == "__main__":
    setup(**config)
