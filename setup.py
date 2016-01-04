#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


# should be loaded below
__version__ = None

with open('ipywatchdogwidget/_version.py') as version:
    exec(version.read())

setup(
    name="ipy-watchdog-widget",
    version=__version__,
    description="Do widget things when watched files change",
    author="Nicholas Bollweg",
    author_email="nick.bollweg@gmail.com",
    license="BSD-3-Clause",
    url="https://github.com/bollwyvl/ipy-watchdog-widget",
    keywords="ipython jupyter watchdog",
    classifiers=["Development Status :: 4 - Beta",
                 "Framework :: IPython",
                 "Programming Language :: Python",
                 "License :: OSI Approved :: BSD License"],
    packages=["ipywatchdogwidget"],
    include_package_data=True
)
