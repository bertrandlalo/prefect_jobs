Mode
====
- Local
- Quetzal

Executor
========
- Sequential
- Synchronous
- Dask

Parameters
==========
- Task Constructor
- Task Run
- Flow

Status
======
- SUCCESS
- SKIP
- FAIL


Cluster
=======

To deploy a docker-compose "cluster" (it's not really a cluster), please follow
these steps:

1. Generate a public/private key with an empty passphrase for github. This is
   needed for the automatic build of a Docker image that contains some of
   OpenMind Innovation Python modules. To generate such key, from iguazu's base
   directory:

   .. code-block:: console

      $ ssh-keygen -t rsa -b 4096 -P "" -f conf/github

   This will create a ``conf/github`` and ``conf/github.pub`` private and public
   key pair, respectively.

2. Add the public key pair contents in ``conf/github.pub`` to your
    `Github SSH keys <https://github.com/settings/ssh/new>`_ settings.

3. Build your docker-compose services.

   .. code-block:: console

      $ docker-compose build
        Building scheduler
        Step 1/19 : FROM python:3.7-slim as intermediate
        ...
        Building scheduler
        Step 1/19 : FROM python:3.7-slim as intermediate
        Step 19/19 : RUN pip install .
         ---> Using cache
         ---> 1c2f33a1c85a
        Successfully built 1c2f33a1c85a
        Successfully tagged iguazu_worker:latest

4. Adapt the worker memory limits if needed on the ``docker.compose.yaml``:

   .. code-block:: yaml

        worker:
          ...
          command: dask-worker --nthreads 1 scheduler:8786 --memory-limit 4GB
          ...

5. Start the docker-compose "cluster" and adapt the number of workers as needed.
   For example, the following command creates a "cluster" with two workers:

   .. code-block:: console

      $ docker-compose up --scale worker=2
