=========
Changelog
=========

This document lists all important changes to iguazu.

Iguazu version numbers follow
`semantic versioning <http://semver.org>`_.

0.1.2 (26-09-2019)
------------------

GSR pipelines

* Remove baseline correction from GSR pipeline. This is something that should
  be done on a analysis-specific post-processing code, probably in a notebook.
* [`#34 <https://github.com/OpenMindInnovation/iguazu/issues/34>`_]
  Add spectral features on galvanic pipeline. Relative and absolute spectra.
* [`#38 <https://github.com/OpenMindInnovation/iguazu/issues/38>`_ ],
  [`#30 <https://github.com/OpenMindInnovation/iguazu/issues/30>`_]
  Improvements on linear regression summaries with a robust regression.
* [`#37 <https://github.com/OpenMindInnovation/iguazu/issues/37>`_ ] fixed
  missing logs due to dask and logging configuration. We still need to be a bit
  more verbose in our code.
* [`#5 <https://github.com/OpenMindInnovation/iguazu/issues/5>`_ ] adapted the
  cvxEDA code to use a moving window, which releases the GIL is more robust.
* [`#36 <https://github.com/OpenMindInnovation/iguazu/issues/36>`_ ] fixed
  missing dependencies to dask by updating to prefect 0.6.1.
* Refactored resampling in galvanic features. Kept 256Hz for the cvxEDA branch
  but uses 512Hz for the spectral branch.
* Rewrite of Iguazu scheduler as kubernetes CronJobs. This seems like a more
  standard solution, but does not profit as well from the cache.
  However, since fixing the cvxEDA problems we are having less problems and
  less need of the cache.

0.1.0 (25-07-2019)
------------------

First version of iguazu.

* Defines structure of package, divided in functions, tasks and flows.

* Added the following pipelines:

  * Local dataset pipeline.
  * Quetzal dataset pipeline.
  * Merged (local or quetzal) dataset pipeline.
  * Galvanic features extraction.
  * Galvanic features summarization (generates population matrix).
  * Behavior features extraction.
  * Behavior features summarization (generates population matrix).

* Command line interface to run, view, schedule flows. Also to generate Docker
  images for deployment in a cluster.

* Kubernetes cluster configuration through helm.
