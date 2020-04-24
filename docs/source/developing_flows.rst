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

      def _build(self, *, foo, bar):
          # Instantiate tasks
          step1 = BarTask()
          step2 = BazTask()
          step3 = FinalTask()

          with self:  # context manager to avoid passing the flow to each task call
              foo_param = Parameter('foo', default=42)
              bar_param = Parameter('bar', default=True)
              many = step1(foo_param, bar_param)  # 1-to-many task
              transformed = step2.map(m=many)     # 1-to-1 task
              reduced = step3(t=transformed)      # many-to-1 task

After creating your flow, you can examine a graph representation of said flow
with:

.. code-block:: console

  $ iguazu flows info myflow

where ``myflow`` is the ``REGISTRY_NAME`` variable of the prepared flow.

Running flows
=============

In order to run a flow, use the following command line:

.. code-block:: console

  $ iguazu flows run myflow

In general, you will need to set some general options *before* the flow name,
while setting flow parameters *after* the flow name. In other words, the
typical command to run a flow will adhere to the following template:

.. code-block:: console

  $ iguazu \
    GENERAL_IGUAZU_OPTIONS \
    flows run \
    GENERAL_RUN_OPTIONS \
    myflow \
    SPECIFIC_FLOW_OPTIONS

Take a look at the ``helm/iguazu/values.yaml``, where you can find many
examples (FYI: these are in fact, the scheduled jobs that are run in a cluster).

The general iguazu options are, as the name indicates, options related to the
general behavior of iguazu, such as logging configuration. You can examine
them with ``iguazu --help``.

General run options are options for how the flow will be executed, such as the
executor type, how cache is used, where the results are saved, etc. You can
examine them with ``iguazu flows run --help``.

Finally specific flow options are flow parameters set by yourself. See the next
section on how to manage them.


Parametrizing flows
===================

In most cases, you will want your flow to accept some parameters that will be
set by command line. These parameters need to be declared on the
``click_options`` method of your flow. This function must return a `tuple` with
all the options (remember that if you have only one option, it still has to be
a tuple, otherwise you will encounter a ``TypeError``).

Parameters are declared using the :py:mod:`click` module.
In the following example, let us assume that the parameters ``foo`` and ``bar``
may be set by command line. This needs to be declared as:

.. code-block:: python

  ...
  import click
  ...


  class MyFlow(PreparedFlow):
      ...

      @staticmethod
      def click_options():
          return (
              click.option('--foo',
                           type=click.STRING, help='Help on foo'),
              click.option('--bar/--no-bar', is_flag=True,
                           help='Turn on or off the bar')
          )

You can now verify how your flow is parametrized with:

.. code-block:: console

  $ iguazu flows run myflow --help
  [2020-02-21 15:50:06]     INFO - root | Iguazu X.Y.Z logging initialized
  Usage: iguazu flows run myflow [OPTIONS]

    Short, one phrase description

  Options:
    --foo             Help of foo
    --bar / --no-bar  Turn on or off the bar
    --help            Show this message and exit.

When you declare parameters this way, the ``**kwargs`` of the ``_build`` function
will be automatically set to the value set by command line. Therefore, you
should change your function signature to add them. **You must set their default
value** (otherwise the help function will fail):

.. code-block:: python

  class MyFlow(PreparedFlow):

      def _build(self, *, foo='default-foo-value', bar=False, **kwargs):
          ...


Combining flows
===============

...


Deploying flows
===============

...
