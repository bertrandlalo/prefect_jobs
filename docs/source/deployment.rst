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

Public/private key
------------------
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

Install G-Cloud
----------------
1. Download the archive file `here <https://cloud.google.com/sdk/docs/quickstart-macos?authuser=2>`_
2. Use the install script to add Cloud SDK tools to your path.

    .. code-block:: console

      $ ./google-cloud-sdk/install.sh


Docker & Kubernetes
-------------------
1. Create an account on  `Docker Hub <https://hub.docker.com>`_.
2. Login to your account:

   .. code-block:: console

      $ docker login

3. Use gcloud to configure a Docker registry. This will enable Docker to push images to GCR.

    .. code-block:: console

           $  gcloud auth configure-docker

4. Finally, install the kubernetes client:

    .. code-block:: console

       $  gcloud components install kubectl

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

   Then, tag a new version in file iguazu/__init__.py.

   Finally, publish them:

   .. code-block:: console

      $ iguazu deploy images --registry eu.gcr.io/GCP_PROJECT_ID

   In our case, our ``GCP_PROJECT_ID`` is ``quetzal-omind``.

3. Create a kubernetes cluster. On minikube, follow the
   `minikube documentation <https://kubernetes.io/docs/setup/learning-environment/minikube/>`_.
   For Google Cloud Platform (GCP), create one with:

   .. code-block:: console

      $ gcloud container clusters create iguazu --num-nodes=1 --machine-type=n1-standard-4

   Optionally, we can add cluster auto scaling to create nodes as the cluster
   needs it, with the options
   ``--enable-autoscaling --min-nodes=1 --max-nodes=N``, where ``N`` is the
   maximum number of nodes.

   Make sure that you have ``kubectl`` installed and that you are
   using the cluster you just created:

   .. code-block:: console

    $ kubectl config get-contexts
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

      $ helm install --name NAME \
          --set-string quetzal.username=USERNAME \
          --set-string quetzal.password=PASSWORD \
          ./helm/iguazu

   where ``NAME`` is an optional name to keep track of helm applications,
   ``USERNAME`` and ``PASSWORD`` are the Quetzal user and password that will
   be used by Iguazu to run its scheduled flows.

   Since we like *Iguazu* as the name of this project, I suggest we use a theme
   here like `names of rivers in alphabetic order <https://en.wikipedia.org/wiki/List_of_rivers_by_length>`_
   (amazon for our first deployment, bluenile when we decide to make a second one, etc.)

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

   $ gcloud container clusters resize iguazu-cluster --num-nodes 0

  bring it back by using the same command with a ``num-nodes`` > 0.

* If you want to resize the cluster to give it more or less resources, use the
  same command but with a number on ``--num-nodes N``. However, if you have
  autoscaling enabled, it will be easier to change the ``dask_worker.replicas``
  entry in the ``helm/iguazu/values.yaml``, followed by an update of the
  deployed chart. To update a chart, see the Updates_ section

* Optionally, you can install the kubernetes dashboard with:

  .. code-block:: console

   $ kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta1/aio/deploy/recommended.yaml

  then, connect to the cluster via a proxy with:

  .. code-block:: console

   $ kubectl proxy

  and explore the dashboard at http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
  The first time you do this, you may need to login by choosing the kube config
  file that is on ``~/.kube/config``.

Updates
-------

If you decide to change something on Iguazu's helm chart (i.e. any file inside
the ``helm/iguazu`` directory, you can update the cluster with:

.. code-block:: console

 $ helm upgrade NAME ./helm/iguazu

where ``NAME`` is the name used when Iguazu was deployed the first time
(see the Deployment_ section, or check with ``helm list``).

Remote execution
----------------

In order to test or debug a new flow or a new image, you may want to run it
locally, using the remote workers and schedulers. To do so, you need to
'create a path' (that's a port) between your computer and the clusters.

To connect to the server running in a Kubectl cluster, you need to 'forward a port'

First:

.. code-block:: console

      $ kubectl get pods
        NAME                                                READY   STATUS    RESTARTS   AGE
        foo-iguazu-dask-scheduler-86d79c57b8-xmt7t          1/1     Running   0          17h
        foo-iguazu-dask-worker-75db98746b-2n2n4             0/1     Pending   0          17h

.. code-block:: console

 $  kubectl port-forward NAME-OF-SCHEDULER  18786:8786

where ``NAME-OF-SCHEDULER`` is the name of the scheduler pod (here `foo-iguazu-dask-scheduler-86d79c57b8-xmt7t`),
``LOCAL-PORT`` is the local port number (eg. 18786) and ``REMOTE-PORT``
is the remote port number (eg. 8786).


Then, in your local iguazu virtual environment, you can run a flow :

.. code-block:: console

 $ iguazu flows run
   --executor-type dask
   --executor-address localhost:LOCAL-PORT  # eg. localhost:18786
   --temp-dir /tmp
   foo-flow  # name of flow
   --data-source quetzal
   --workspace-name foo-workspace # name of quetzal workspace


Triggering a job
----------------

If may be useful to trigger a job manually. To do this, first check the list of
existing jobs:

.. code-block:: console

 $ kubectl get cronjobs -l app=iguazu
   NAME                               SCHEDULE     SUSPEND   ACTIVE   LAST SCHEDULE   AGE
   foo-iguazu-job-behavior-features   0 2 * * *    True      0        <none>          6m23s
   foo-iguazu-job-behavior-summary    0 14 * * *   True      0        <none>          6m23s
   foo-iguazu-job-galvanic-features   0 1 * * *    True      0        <none>          6m23s
   foo-iguazu-job-galvanic-summary    0 13 * * *   True      0        <none>          6m23s

Then, create the job that you want with:

.. code-block:: console

 $ kubectl create job --from=cronjob/NAME MANUAL_NAME

where ``NAME`` is the name on the list above and ``MANUAL_NAME`` is some
identifier that you choose to keep track of you job.


Kubernetes logs
---------------

While using ``kubectl logs POD_NAME`` is a quick way to get the logs of a pod,
you can also install `kubetail <https://github.com/johanhaleby/kubetail>`_ and
get live, updated logs with:

.. code-block:: console

 $ kubetail iguazu
