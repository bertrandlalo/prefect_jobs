.. _`Creating new tasks`:

==================
Creating new tasks
==================

... to write next time I write a new task ...

Things to remember:

* If you overwrite the :py:meth:`~iguazu.core.tasks.Task.preconditions`
  method, don't forget to call its parent implementation so that your task can
  benefit from output reuse and forced tasks management.
