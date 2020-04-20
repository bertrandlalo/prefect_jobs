======
Iguazu
======

|test-status|

Open Mind Innovation Python jobs platform.
Using `Prefect <https://www.prefect.io/>`_ to handle the definition, composition
and execution of tasks as data processing pipelines, or more simply, *flows*.

.. pull-quote::

    The name "Iguazú" comes from the Guarani or Tupi words "y" [ɨ], meaning "water",
    and "ûasú "[waˈsu], meaning "big".[3] Legend has it that a deity planned to
    marry a beautiful woman named Naipí, who fled with her mortal lover Tarobá in a
    canoe. In a rage, the deity sliced the river, creating the waterfalls and
    condemning the lovers to an eternal fall.

Installation
------------

For development
^^^^^^^^^^^^^^^

If you want to develop Iguazu, the recommended approach is to
`install poetry <https://python-poetry.org/docs/#installation>`_, clone this
repository and install it:

.. code-block:: bash

   $ git clone https://github.com/OpenMindInnovation/iguazu.git
   $ cd iguazu
   $ poetry install

If you prefer using conda, ``environment.yaml`` is provided in this repository,
but you should still use poetry for editable installs (there is no
``pip install -e`` but ``poetry install`` does the same thing).


As a library
^^^^^^^^^^^^

Installing Iguazu as a library only needs you to add the following line to
your ``requirements.txt``:

.. code-block:: text

   git+https://github.com/OpenMindInnovation/iguazu.git@vX.Y.Z#egg=iguazu

where ``vX.Y.Z`` is the exact version number that you need.

For conda users, add it on the ``pip`` section of your ``environment.yaml``:

.. code-block:: yaml

    name: ...
    dependencies:
    - pip
    - pip:
        - git+https://github.com/OpenMindInnovation/iguazu.git@vX.Y.Z#egg=iguazu

Documentation
-------------

A readthedocs server is coming soon.


Contribute
----------

- Issue Tracker https://github.com/OpenMindInnovation/iguazu/issues
- Source Code: https://github.com/OpenMindInnovation/iguazu

.. |test-status| image:: https://github.com/OpenMindInnovation/iguazu/workflows/unit%20tests/badge.svg?branch=master
    :alt: Automatic unit tests status (on master)
    :scale: 100%
    :target: https://github.com/OpenMindInnovation/iguazu/actions
