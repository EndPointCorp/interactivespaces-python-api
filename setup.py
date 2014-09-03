#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='interactivespaces-python-api',
    version='1.6.2',
    author='Wojciech Ziniewicz',
    author_email='wojtek@endpoint.com',
    packages=['interactivespaces'],
    scripts=[],
    url='http://pypi.python.org/pypi/interactivespaces-python-api',
    license='LICENSE.txt',
    description='Interactivespaces ',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.3.0",
        "nosy >= 1.1.2",
        "mock"
    ]
)
