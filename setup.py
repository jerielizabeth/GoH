# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='GoH',
      version='0.1',
      description='Dissertation related functions and utilities',
      long_description=readme(),
      url='',
      author='Jeri Wieringa',
      author_email='',
      license='MIT',
      packages=['GoH'],
      install_requires=[
          'beautifulsoup4',
          'nltk <= 3.2.2',
          'pandas <=0.19.2',
          'pyxdameraulevenshtein', 
          # 'gensim >= 0, < 2',
          'textblob',
          # 'scipy >= 0.16, < 0.18',
          # 'numpy <= 1.12.0'
      ],
      zip_safe=False)