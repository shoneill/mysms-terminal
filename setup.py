#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mysmsterminal

setup(name='mysms-terminal',
      version=mysmsterminal.VERSION,
      license=mysmsterminal.LICENSE,
      scripts=['bin/mysms-terminal'],
      packages=('mysmsterminal',
                'mysmsterminal.api')
     )
