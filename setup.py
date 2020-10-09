# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='adsapi',
      version='201008.1',
      url='https://www.dafnet.se',
      author='David Stenwall',
      author_email='david.stenwal@icloud.com',
      packages=[
          'adsapi'
      ],
      include_package_data=True,
      install_requires=[
          'Flask',
          'SQLAlchemy',
          'flask-cors',
          'email_validator',
          'pytest'
      ]
      )
