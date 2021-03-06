.. _`Versioning`:

==========
Versioning
==========

If you are developing on Iguazu, please follow these guidelines on how to
organize versions. Read the general guidelines below, then read the proposed
workflow at the end of this document.

General versioning guidelines
=============================

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
using ``bump2version``. Do read the workflow at the end of this document for
more guidelines.

.. code-block:: bash

   # Bumps the patch version because we are fixing a bug
   $ bump2version --verbose patch
   current version=0.4.0
   ...
   new_version=0.4.1

   # or...
   $ bump2version --verbose minor
   current_version=0.4.1
   ...
   new_version=0.5.0

You will notice that if your local git repository is **dirty** (i.e. it has
uncommited chages), this command will fail. You will need to commit your changes
first or use the ``--allow-dirty`` flag. Prefer the former.

After ``bump2version`` succeeds, you will notice that some files have been
automatically updated:

.. code-block:: bash

   $ git status
    On branch blabla
    Changes not staged for commit:
      (use "git add <file>..." to update what will be committed)
      (use "git checkout -- <file>..." to discard changes in working directory)

            modified:   .bumpversion.cfg
            modified:   helm/iguazu/Chart.yaml
            modified:   helm/iguazu/values.yaml
            modified:   iguazu/__init__.py
            modified:   pyproject.toml

Review the changes with ``git diff`` and you will see that the version string
has been updated on all relevant places. You can add more files on the
``.bumpversion.cfg`` configuration file, but this will rarely be necessary.

You can now commit and tag. Or, you can reset your changes. Or, you can
reset your changes and let ``bump2version`` do the commit and tag automatically:

.. code-block:: bash

   # Reset the changes introduced just before. CAREFUL, if you have more
   # changes, you will lose them!
   $ git reset --hard HEAD

   # Use bump2version automatic commit and tag:
   $ bump2version --commit --tag minor

   # Use git to verify your commit and tag:
   $ git log --pretty=oneline --abbrev-commit
   2575233 Bump version: 0.4.0 → 0.5.0

   # Use git to push and push the tags
   git push --tags

Some final notes:

* Avoid pushing tags for build versions. This is useful for development, but not
  for our git repository.
* You will almost never bump the major version, unless there is a major change
  that affects everything.
* You will not need to change the version on all of the files that use it or
  declare it, but do review these changes before pushing, just in case.
* Ultimately, the version number that sets all the other ones should be one
  on the ``.bumpversion.cfg`` file. If the ``bump2version`` command fails, it
  is probably the ``current_version`` property is incorrect.


Versioning workflow
===================

Use the following workflow as a guideline on your developments:

1. Start by creating a branch for your new work.

2. Bump the *build* version, but do not commit or tag yet.

3. Develop your code.

4. Test locally. Repeat until you are satisfied (is your code stable?).

5. Build Iguazu (i.e. create the images, etc.) so you can test on the
   development cluster. If there are errors or problems, repeat steps 2-5.

   When your code has been tested on the development servers, then it is
   ready for production.

6. Commit all your changes, and request a pull request. Repeat the previous
   steps if the pull request reviewer comments require it.

Production versioning guideline:

1. Depending on the final scope of the changes (was it just a bug fix or a
   new feature?), bump the patch or minor version. Your version string should
   now be only a ``MAJOR.MINOR.PATCH`` string, that is, no build part is
   present.

2. Commit and tag the changes. Do not use *dirty* git repositories for the next
   steps.

3. Build and deploy.
