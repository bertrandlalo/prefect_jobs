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


Preparations
============

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

Docker-compose
==============

A docker-compose "cluster" (it's not really a cluster) is a simple environment
to test iguazu and dask. To create this environment, follow these steps:

1. Make sure you followed the Preparations_ instructions to create a private and
   public key pair.

2. Build your docker-compose services.

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

3. Adapt the worker memory limits if needed on the ``docker.compose.yaml``:

   .. code-block:: yaml

        worker:
          ...
          command: dask-worker --nthreads 1 scheduler:8786 --memory-limit 4GB
          ...

4. Start the docker-compose "cluster" and adapt the number of workers as needed.
   For example, the following command creates a "cluster" with two workers:

   .. code-block:: console

      $ docker-compose up --scale worker=2


Kubernetes
==========


To deploy on a kubernetes cluster (in this case using Google Cloud Platform),
follow these instructions. If you already have set up a iguazu cluster, you can
skip the steps on the first section.

Setup
-----

1. Make sure you followed the Preparations_ instructions to create a private and
   public key pair.

2. Publish the Iguazu Docker images to a registry. In this case, the
   Google Cloud Registry. First, make sure that the Docker images can be built
   successfully:

   .. code-block:: console

      $ docker build .

   Then, publish them:

   .. code-block:: console

      $ iguazu deploy images --registry eu.gcr.io/GCP_PROJECT_ID

   In our case, our ``GCP_PROJECT_ID`` is ``quetzal-omind``.

3. Create a kubernetes cluster. On minikube, follow the
   `minikube documentation <https://kubernetes.io/docs/setup/learning-environment/minikube/>`_.
   For Google Cloud Platform (GCP), create one with:

   .. code-block:: console

      $ gcloud container clusters create iguazu --num-nodes=1 --machine-type=n1-standard-4

   On either case, make sure that you have ``kubectl`` installed and that you are
   using the cluster you just created:

   .. code-block:: console

      $ kubectl config get-context
      CURRENT   NAME                                       CLUSTER                                    AUTHINFO                                   NAMESPACE
      *         gke_quetzal-omind_europe-west1-c_iguazu    gke_quetzal-omind_europe-west1-c_iguazu    gke_quetzal-omind_europe-west1-c_iguazu

4. Install `Helm <https://helm.sh/>`_ on your local computer.  In general,
   follow the `installing helm guide <https://helm.sh/docs/using_helm/#installing-helm>`_.
   For the particular case of OSX (with homebrew), this can be done with:

   .. code-block:: console

    $ brew install kubernetes-helm

5. Install helm k8s service account. This is explained in the
   `helm installation guide <https://helm.sh/docs/using_helm/#tiller-and-role-based-access-control>`_:

   .. code-block:: console

    $ kubectl create -f helm/rbac-config.yaml

6. Install helm k8s resources (also known as tiller) with a service account:

   .. code-block:: console

    $ helm init --service-account tiller --wait

7. Verify that helm was correctly installed:

   .. code-block:: console

    $ helm version
    Client: &version.Version{SemVer:"v2.14.3", GitCommit:"0e7f3b6637f7af8fcfddb3d2941fcc7cbebb0085", GitTreeState:"clean"}
    Server: &version.Version{SemVer:"v2.14.3", GitCommit:"0e7f3b6637f7af8fcfddb3d2941fcc7cbebb0085", GitTreeState:"clean"}

8. Install ingress resources and the ingress chart. There are more details in
   the `ingress installation guide <https://kubernetes.github.io/ingress-nginx/deploy/#prerequisite-generic-deployment-command>`_.

   .. code-block:: console

    $ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml
    $ helm install stable/nginx-ingress --name nginx-ingress

Deployment
----------

1. Install the Helm chart into the kubernetes cluster to deploy the Iguazu application:

   .. code-block:: console

      $ helm install --name somename \
          --set-string quetzal.username=USERNAME \
          --set-string quetzal.password=PASSWORD \
          ./helm/iguazu

   where ``somename`` is an optional name to keep track of helm applications,
   ``USERNAME`` and ``PASSWORD`` are the Quetzal user and password that will
   be used by Iguazu to run its scheduled flows.

2. Get the scheduler service external IP if you want to see the UI. It will be
   listed on the ``EXTERNAL-IP`` of the ``nginx-ingress-controller`` service.

   .. code-block:: console

      $ kubectl get services
        NAME                            TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)                      AGE
        dask-scheduler                  ClusterIP      10.47.248.79   <none>           8786/TCP,8787/TCP            4m12s
        kubernetes                      ClusterIP      10.47.240.1    <none>           443/TCP                      41m
        nginx-ingress-controller        LoadBalancer   10.47.250.82   XXX.XXX.XXX.XXX  80:30439/TCP,443:32645/TCP   34m
        nginx-ingress-default-backend   ClusterIP      10.47.245.99   <none>           80/TCP                       34m

   You can open a browser at ``https://XXX.XXX.XXX.XXX/`` to see the dask UI.


Post-installation
-----------------

* If you want to pause the cluster on GCP:

  .. code-block:: console

   $ gcloud container clusters resize iguazu-cluster --size 0

  bring it back by using the same command with a size > 0.


* If you want to resize the cluster to give it more or less resources, use the
  same command but with a number on ``--size N``.
