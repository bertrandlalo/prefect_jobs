.. _`Creating new flows`:

==================
Creating new flows
==================

When creating a new flow, you need to sit down for a bit to think what you want
to express as a flow, by carefully defining how you plan to divide your problem
into three concepts: functions, tasks and a flow.
Read the :ref:`Key concepts` and :ref:`Guidelines` to understand these nuances
between these concepts.

The main use case of a flow is to orchestrate several tasks.

Quickstart
==========

To create a new flow, start by creating or extending the appropriate file on
``iguazu/flows`` and following this template:

.. code-block:: python

  from iguazu.core.flows import PreparedFlow


  class MyFlow(PreparedFlow):
      """Short, one phrase description

      Long description
      """

      REGISTRY_NAME = 'myflow'


By using a :py:class:`iguazu.core.flows.PreparedFlow` and setting its
class attribute
:py:attr:`REGISTRY_NAME <iguazu.core.flows.PreparedFlow.REGISTRY_NAME>`,
this class will be automatically associated to the Iguazu flow registry.
This means you can use it on the command line:

.. code-block:: console

  $ iguazu flows list
  List of registered flows
                              DESCRIPTION
  NAME
  myflow    Short, one phrase description

If you try to run it with ``iguazu flows run myflow`` at this point, it will
fail because the flow is still not being built. In other words, you have not yet
declared what this flow does. You will do this by implementing the ``_build``
function:

.. code-block:: python

  from prefect import Parameter

  from iguazu.core.flows import PreparedFlow
  from iguazu.tasks.example import BarTask, BazTask


  class MyFlow(PreparedFlow):
      """Short, one phrase description

      Long description
      """

      REGISTRY_NAME = 'myflow'

      def _build(self, **kwargs):
          # Instantiate tasks
          step1 = BarTask()
          step2 = BazTask()

          with self:  # context manager to avoid passing the flow to each task call
              foo = Parameter('param', default='foo')
              bars = step1(foo)
              bazs = step2.map(bars)

Running flows
=============

...


Combining flows
===============

...


Deploying flows
===============

...
