.. _`Versioning`:

==========
Versioning
==========

If you are developing on Iguazu, please follow these guidelines on how to
organize versions.

Iguazu follows a SemVer versioning scheme. That means that versions have
MAJOR, MINOR and PATCH part, and they look like look like ``1.5.2``. In this
example, the MAJOR is 1, MINOR is 5 and PATCH is 2. Major version numbers
increase when there is a large, backward-incompatible change. Minor version
numbers increase when there is a new feature and backward-compatibility is
maintained. Patch version numbers increase when there is a bug or small change
on existing code.

You can read on Iguazu version history on the :ref:`Changelog`.

When versions are not stable yet, there may be a prerelease or build part on
the version string: ``1.5.2-alpha`` or ``1.5.2-beta.3``.
Here, ``alpha`` or  ``beta`` are the prerelease part, and
``3`` is the build number part.

The problem with versioning is that we are setting the version number in
several files. This eventually leads to errors due to forgetting to change one
file among the set of all files that need to be changed. To address this, we
are using ``bump2version``. Use it as explained below.

When developing of a new feature of Iguazu, **bump** the version accordingly
using ``bump2version``:

.. code-block:: bash

   # Bumps the patch version because we are fixing a bug
   $ bump2version --verbose patch
   current version=0.4.0
   new_version=0.4.1

   # or...
   $ bump2version --verbose minor
   current_version=0.4.1
   new_version=0.5.0


You will notice that if your local git repository is **dirty** (i.e. it has
uncommited chages), this command will fail
