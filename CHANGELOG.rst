=========
Changelog
=========

This document lists all important changes to iguazu.

Iguazu version numbers follow
`semantic versioning <http://semver.org>`_.

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
