===========================
Deployment on a k8s cluster
===========================

This document will help you build and deploy a kubernetes cluster. The following
diagram represents how this cluster works and how it interacts with Quetzal:

.. figure:: _static/Data\ tools.png
 :alt: Cluster diagram
 :width: 75%



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

   Optionally, we can add cluster auto scaling to create nodes as the cluster
   needs it, with the options
   ``--enable-autoscaling --min-nodes=1 --max-nodes=N``, where ``N`` is the
   maximum number of nodes.

   Make sure that you have ``kubectl`` installed and that you are
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
