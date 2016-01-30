#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.1'

setup(
    name='example',
    version=version,
    author='',
    author_email='cyb@example.me',
    packages=[
        'example',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.7.1',
    ],
    zip_safe=False,
    scripts=['example/manage.py'],
)
