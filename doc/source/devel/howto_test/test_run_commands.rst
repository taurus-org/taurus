
.. currentmodule:: sardana.test.

.. _sardana-test-run-commands:


===========================
Run tests from command line
===========================


Run the whole Sardana test suite
--------------------------------

Running the whole Sardana test suite from command line can be done by going 
to the Sardana directory:
<sardana_root>/sardana/test/.

And executing:
python testsuite.py



Run a single test
-----------------

Executing a single test from command line is done by doing:
    python -m unittest test_name

Where test_name is the test module that has to be run.

That can be done with more verbosity by indicating the option -v.
    python -m unittest -v test_name 


