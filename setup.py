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
          'nltk <= 3.2.2',
          'pandas <= 0.19.2',
          'gensim == 3.1.0',
          'textblob',
          'scipy <= 0.19.0',
          # 'numpy <= 1.12.0'
          'bokeh == 0.12.5',
          'seaborn',
          'pyxdameraulevenshtein',
          'matplotlib == 2.0.2'
      ],
      zip_safe=False)