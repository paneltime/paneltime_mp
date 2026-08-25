#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

version = '0.0.3'

from setuptools import setup, find_packages
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()


setup(
    name='paneltime_mp',
    version=version,
    description='Multiprocessing interface',
    long_description=long_description,
  long_description_content_type='text/markdown',
    url='https://github.com/espensirnes/paneltime_mp',
    author='Espen Sirnes',
    author_email='espen.sirnes@uit.no',
    license='GPL-3.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8',
        ],

    keywords='econometrics',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    extras_require={'linux': ['gcc']},

)

