Collection of functions used in my dissertation, *A Gospel of Health and Salvation*. 


Examples
--------

To generate error rate statistics:

.. code-block:: python

	import GoH.reports

	GoH.reports.process_directory(directory, spelling_dictionary)

To create a spelling dictionary from text files:

.. code-block:: python

	import GoH.utilities

	GoH.utilities.create_spelling_dictionary(wordlists, directory)

`wordlists` is a list of file(s) containing the verified words and `directory` is the directory where those wordlist files reside. This function converts all words to lowercase and returns only the list of unique entries.


Installation
------------

I am primarily distributing this library in order to share the computational work of my dissertation and enable it to be repeated and reused. This is not a particularly well formed or generalized library and so I am not distributing via `PyPI <https://pypi.python.org/pypi>`_. 

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


License
-------