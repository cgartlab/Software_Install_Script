#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Software Install Script Setup
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='software-install-script',
    version='0.1.0',
    description='A cross-platform software installation tool with CLI and TUI interfaces',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='cgartlab',
    author_email='',
    url='https://github.com/cgartlab/Software_Install_Script',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'rich',
        'pyyaml',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'sis = sis.main:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)