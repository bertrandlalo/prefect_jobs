======
Iguazu
======

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

Install this package by adding the following line to your
``environment.yaml`` file as follows:

.. code-block:: yaml

    name: ...
    dependencies:
    - pip
    - pip:
        - git+ssh://git@github.com/OpenMindInnovation/iguazu.git@vX.Y.Z#egg=iguazu
        # or
        - git+https://github.com/OpenMindInnovation/iguazu.git@vX.Y.Z#egg=iguazu

where ``vX.Y.Z`` is the exact version number that you need.

If you want to develop on iguazu *at the same time* that you are
developing some other project, clone this repository and install it on
development mode:

.. code-block:: console

    $ git clone git+ssh://git@github.com/OpenMindInnovation/iguazu.git
    $ cd iguazu
    $ pip install -e .

Note that this *development mode* is not recommended for reproducible analyses
because you might end up with a locally modified version that is not available
to other people.

Documentation
-------------

A readthedocs server is coming soon.


Contribute
----------

- Issue Tracker https://github.com/OpenMindInnovation/iguazu/issues
- Source Code: https://github.com/OpenMindInnovation/iguazu
