#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


with open('requirements_dev.txt') as requirements_file:
    requirements = list(requirements_file.readlines())

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Akshay Aithal",
    author_email='akshay.aithal@gkndriveline.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description="Tool to initialize and  sync all the svn repo",
    entry_points={
        'console_scripts': [
            'svn_sync_tool=svn_sync_tool.cli:svn_sync_tool',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='svn_sync_tool',
    name='svn_sync_tool',
    packages=find_packages(include=['svn_sync_tool']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/audreyr/svn_sync_tool',
    version='0.3.9',
    zip_safe=False,
)
