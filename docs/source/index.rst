Iguazu: a toolbox for data science processing pipelines
=======================================================

Iguazu is a Python library that gathers, connects and orchestrates data storage,
offline analysis processing pipelines, and cloud computing resources. It
leverages key open-source libraries, frameworks and tools to help data
scientists create high-quality, peer-reviewed, reproducible datasets, while
helping data engineers develop and maintain the processing pipelines that
generate these datasets.
*Standing in the shoulders of giants*, Iguazu uses the standard Python
data-science libraries (NumPy, SciPy, Pandas) combined with domain-specific
libraries (scikit-learn, MNE, Neurokit), orchestrated by a new promising
data engineering framework (Prefect) based on well-established parallelization
library (Dask), and deployed with cloud-based big players (Kubernetes, Helm).

Iguazu uses *Flows* to orchestrate *Tasks*. There are many *flows*, and behind
all of these concurrent *flows*, there might be a rainbow showing a treasure,
hence the name:

.. epigraph::

   Iguazú Falls or Iguaçu Falls (Spanish: Cataratas del Iguazú [kataˈɾatas ðel iɣwaˈsu];
   Guarani: Chororo Yguasu [ɕoɾoɾo ɨɣʷasu]; Portuguese: Cataratas do Iguaçu
   [kataˈɾatɐs du iɡwaˈsu]) are waterfalls of the Iguazu River on the border of
   the Argentine province of Misiones and the Brazilian state of Paraná. Together,
   they make up the largest waterfall system in the world.[2]
   The falls divide the river into the upper and lower Iguazu.

   The name "Iguazú" comes from the Guarani or Tupi words "y" [ɨ], meaning "water",
   and "ûasú "[waˈsu], meaning "big".[3] Legend has it that a deity planned to marry
   a beautiful woman named Naipí, who fled with her mortal lover Tarobá in a canoe.
   In a rage, the deity sliced the river, creating the waterfalls and condemning the
   lovers to an eternal fall.[3] The first European to record the existence of the
   falls was the Spanish Conquistador Álvar Núñez Cabeza de Vaca in 1541.

   -- `Wikipedia, Sept 2019 <https://en.wikipedia.org/wiki/Iguazu_Falls>`_


.. toctree::
   :maxdepth: 1
   :caption: General documentation

   key_concepts
   guidelines
   hdf5
   developing_tasks
   developing_flows

.. toctree::
   :maxdepth: 1
   :caption: Specifications

   specs/signals
   specs/events
   specs/features

.. toctree::
   :maxdepth: 1
   :caption: Deployment

   deployment

.. toctree::
   :maxdepth: 6
   :caption: API

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

