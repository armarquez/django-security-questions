#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import django_security_questions

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = django_security_questions.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='Django-security-questions',
    version=version,
    description="""Django security questions is a simple Django app to include security questions into your user models""",
    long_description=readme + '\n\n' + history,
    author='Anthony Marquez',
    author_email='anthony.marquez@praetorian.com',
    url='https://github.com/praetorianlabs-amarquez/django-security-questions',
    packages=[
        'django_security_questions',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-security-questions',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)