# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='GoH',
      version='0.5',
      description='Dissertation related functions and utilities',
      long_description=readme(),
      url='',
      author='Jeri Wieringa',
      author_email='',
      license='MIT',
      packages=['GoH'],
      install_requires=[
          'beautifulsoup4',
          'bokeh == 0.12.5',
          'gensim == 3.1.0',
          'matplotlib == 2.0.2',
          'nltk <= 3.2.2',
          # 'numpy <= 1.12.0'
          'pandas <= 0.19.2',
          'pyxdameraulevenshtein',
          'scipy <= 0.19.0',
          'seaborn',
          'sklearn',
          'textblob'
      ],
      zip_safe=False)