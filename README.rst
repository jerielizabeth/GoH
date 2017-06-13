==========
GoH
==========

Collection of functions used in my dissertation, *A Gospel of Health and Salvation*. 

Available sections of the module are: 

+ charts -- code for generating data visualizations
+ clean -- code for cleaning messy OCR
+ compile -- code for generating data about the corpus
+ model -- code creating topic modeling pipeline
+ normalize -- code for standardizing the text
+ reports -- code for taking the data about the corpus and isolating particular elements
+ utilities -- helper functions for executing the above tasks.


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

To install, navigate to the root directory of module (GoH/) and run

.. code-block::
	
	pip install .


To update, run

.. code-block::
	
	pip install --upgrade .

If you are using with the dissertation conda environment, a version of this code is already included in the environment. To ensure that you have the latest version, run the update command before executing the notebooks.

Usage
-----


License
-------