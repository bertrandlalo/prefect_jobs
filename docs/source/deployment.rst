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


Clusters
========

Docker-compose
--------------

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


Kubernetes
----------

To deploy on kubernetes (either a Google Cloud Platform or a local minikube),
follow these instructions:

1. Make sure to follow steps 1 and 2 on the docker-compose section above.

2. Publish the Iguazu Docker images to a registry. In
   this case, the Google Cloud Registry:

   .. code-block:: console

      $ python iguazu/cli.py --registry gcr.io/your-gcp-project-id

3. Create a kubernetes cluster. On minikube, follow the
   `minikube documentation <https://kubernetes.io/docs/setup/learning-environment/minikube/>`_.
   For Google Cloud Platform (GCP), create one with:

   .. code-block:: console

      $ gcloud container clusters create iguazu-cluster --num-nodes=1 --machine-type=n1-standard-4

   On either case, make sure that you have ``kubectl`` installed and that you are
   using the cluster you just created:

   .. code-block:: console

      $ kubectl config get-context
      CURRENT   NAME                 CLUSTER             AUTHINFO                                                      NAMESPACE
      *         xxx_iguazu-cluster   xxx_iguazu-cluster  xxx_iguazu-cluster

4. Install `Helm <https://helm.sh/>`_ on your local computer.

5. Deploy *Tiller* (the Helm kubernetes application) on your kubernetes cluster with:

   .. code-block:: console

      $ helm init

6. Install the Helm chart into the kubernetes cluster to deploy the Iguazu:

   .. code-block:: console

      $ helm install --name somename \
          --set-string quetzal.username=USERNAME \
          --set-string quetzal.password=PASSWORD \
          ./helm/iguazu

   where ``somename`` is an optional name to keep track of helm applications,
   ``USERNAME`` and ``PASSWORD`` are the Quetzal user and password that will
   be used by Iguazu to run its scheduled flows.

7. Get the scheduler service external IP. This is the IP that you will need to
   use as the dask scheduler.

   .. code-block:: console

      $ kubectl get services
      NAME                        TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                       AGE
      somename-iguazu-scheduler   LoadBalancer   10.47.255.179   35.240.37.119   8786:30392/TCP,80:31366/TCP   67s

8. If you want to pause the cluster on GCP:

   .. code-block:: console

      $ gcloud container clusters resize iguazu-cluster --size 0

   bring it back by using the same command with a size > 0.
