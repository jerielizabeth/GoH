I created a series of modules to house and distribute a collection of functions I use in my dissertation, *A Gospel of Health and Salvation*. These modules are necessary for running the processes documented in `notebooks repository <https://github.com/jerielizabeth/Gospel-of-Health-Notebooks>`_, where I document my processes and analysis. I have focused on documenting the function variables and the ways they work together so that they can be evaluated and, if possible, modified for use in other contexts. It is important to note, however, that I developed these functions to work on the particular dataset of my dissertation and to answer particular questions, and that they will likely require modification to be generalizable to other problem spaces.

Examples
--------

To generate error rate statistics:

.. code-block:: python

	import GoH.describe

	GoH.describe.process_directory(directory, spelling_dictionary)

To create a spelling dictionary from text files:

.. code-block:: python

	import GoH.utilities

	GoH.utilities.create_spelling_dictionary(wordlists, directory)

`wordlists` is a list of file(s) containing the verified words and `directory` is the directory where those wordlist files reside. This function converts all words to lowercase and returns only the list of unique entries.


Installation
------------

I am primarily distributing this library in order to share the computational work of my dissertation and enable it to be repeated and reused. This is not a particularly well-formed or generalized library and so I am not distributing via `PyPI <https://pypi.python.org/pypi>`_. 

If you are using this library with my `Dissertation notebooks <https://github.com/jerielizabeth/Gospel-of-Health-Notebooks>`_, I recommend following the instructions on that repository for setting up and activating a local environment with Conda prior to installing the GoH library.

You can install the library by cloning the repository, navigating to the root directory of module (GoH/), and running:  

.. code-block:: bash
	
	pip install .


Be sure that the environment is active prior to installation.

To update, run:

.. code-block:: bash
	
	pip install --upgrade .


Usage
-----

Each module contains a collection of functions to be used individually or in sequence to perform the different computational tasks involved in aggregating, preparing, modeling, and analyzing the periodical literature of the Seventh-day Adventist church for my dissertation. See module introductions for particular use instructions. 

License
-------

The project is available as open source under the terms of the `MIT License <LICENSE>`_.