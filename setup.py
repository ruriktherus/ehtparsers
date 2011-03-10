#!/usr/bin/env python

from setuptools import setup

setup(name='vlbidata',
      version='1.0',
      description='Python VLBI Management Utilities',
      author='Rurik A. Primiani',
      author_email='rprimian@cfa.harvard.edu',
      packages=['vlbidata',
                'vlbidata.tsys'],
      py_modules=['ipy_vlbidata'],
     )
