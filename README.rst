===========
pytest-pudb
===========

Pytest PuDB debugger integration based on pytest `PDB integration`_


Use it as ``--pdb`` ``py.test`` command argument:


.. code-block:: console

    py.test --pudb

Or simply use ``pudb.set_trace`` inside your python code:

.. code-block:: python

    def test_set_trace_integration():
        # No --capture=no need
        import pudb
        pudb.set_trace()
        assert 1 == 2

    def test_pudb_b_integration():
        # No --capture=no need
        import pudb.b
        # traceback is set up here
        assert 1 == 2


See also `pytest`_ and `pudb`_ projects.


.. _PDB integration: http://doc.pytest.org/en/latest/usage.html#dropping-to-pdb-python-debugger-on-failures
.. _pudb: https://pypi.python.org/pypi/pudb
.. _pytest: https://pypi.python.org/pypi/pytest
