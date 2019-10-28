=====================
Feature specification
=====================

========= ==========
Status    PROPOSAL
--------- ----------
Authors   David
--------- ----------
Reviewers
--------- ----------
Version   0
--------- ----------
Date      2019-10-23
========= ==========


The specification aims to standardize how *features* are represented so that
any function that generates *features* can follow the structure described in
this document.

Notation
========

Features and observations
-------------------------

In a general sense, a feature is a value of an observable phenomenon. For the
purposes of Iguazu, a feature is value associated to an observation.

An observation is a reference. It can be a specific time instant,
a time segment, a session. An observation can also be unrelated to time:
a subject, a population, etc.
The definition of observation depends on the application or objective of an
analysis.

Scope
=====

Since features are calculated by different functions, this document defines how
any feature generation code should represent these features. This will help
homogeneize any downstream task that receive these features.

This specification is designed to accomodate our current feature use-cases:
one feature value per *sequence*, while permitting new use-cases on the future,
in particular *dynamic* features (the observation reference is a time window)
It also permits the extension of feature-related information through metadata.

The feature specification is also designed to address how a large number of
features can be handled in parallel. In particular, *wide* dataframes
(when the number of columns is larger than the number of rows) are more
difficult to divide, whereas *long* dataframes (when the number of rows is
larger than the number of columns) are easier to partition (e.g. with a
map/reduce pattern).

Specification
=============

Storage
-------

Following the :ref:`Guidelines` concerning :ref:`rule_file_format`,
the preferred format to save standard Iguazu features is a
:py:class:`pandas.DataFrame` embedded in a HDF5 file under a key as defined
in the :ref:`hdf5`. The preferred HDF5 key for  is
``/iguazu/features/modality/reference``, where ``modality`` is the source
of the data (e.g. gsr, ppg, ecg, eeg, etc.) and ``reference`` is the
observation reference (e.g. epoch, sequence, session, subject).

Contents
--------

A feature dataframe is defined as follows:

#. It MUST have exactly two dimensions.

#. It MUST have the following columns:

   * A column named *id* of type object and string contents. It is an identifier
     for a feature and it MUST be unique across all features.

   * A column named *value* containing the value of the feature. There is no
     restriction on the type, since features can be numeric or structural, but
     in most cases it SHOULD be a numeric type. The value type SHOULD be
     homogeneous (e.g. avoid mixing numeric and string types).

   * A column named *reference* containing an identifier to the observation
     reference.

#. Additionally, it SHOULD have the following columns:

   * A column named *name* of type object with string contents. It is a human
     readable representation of the *id* column and it MAY be unique across all
     features (but we will probably quickly reach a point where it will not
     make sense to maintain the uniqueness of the name).

   * A column named *file_id*, to be used for keeping a reference to the
     original raw file that was used to generate this feature, if any. While
     this column is optional, it is very important to relate and enrich features
     with metadata from other systems such as Quetzal.

#. Any other additional column is permitted. They can be used to attach metadata
   to the features. An useful example is to provide details on bad values: the
   *value* column can be NaN, and a *extra* column could indicate what the NaN
   represents for a particular observation.

Examples
========

The following dataframe conforms to this specification:

.. code-block:: pycon

   >>> print(features)

         reference            id     value              name                               file_id units      nan_details
    0   baseline_1        ppg_HR -0.186326        Heart rate  c41da942-837f-4b46-b1e7-c08ea5e1d1d9   bpm             None
    1   baseline_1  gsr_peakrate  0.739373     Phasic blabla  c41da942-837f-4b46-b1e7-c08ea5e1d1d9    au             None
    2   baseline_1      respi_Ti -0.123698  Inspiration time  c41da942-837f-4b46-b1e7-c08ea5e1d1d9     s             None
    3       task_1        ppg_HR       NaN        Heart rate  c41da942-837f-4b46-b1e7-c08ea5e1d1d9   bpm  Not enough data
    4       task_1  gsr_peakrate  0.934251     Phasic blabla  c41da942-837f-4b46-b1e7-c08ea5e1d1d9    au             None
    5       task_1      respi_Ti  0.653636  Inspiration time  c41da942-837f-4b46-b1e7-c08ea5e1d1d9     s             None
    6       task_2        ppg_HR       NaN        Heart rate  c41da942-837f-4b46-b1e7-c08ea5e1d1d9   bpm       Artifacted
    7       task_2  gsr_peakrate -0.171955     Phasic blabla  c41da942-837f-4b46-b1e7-c08ea5e1d1d9    au             None
    8       task_2      respi_Ti  0.055566  Inspiration time  c41da942-837f-4b46-b1e7-c08ea5e1d1d9     s             None
    9   baseline_2        ppg_HR -0.410132        Heart rate  c41da942-837f-4b46-b1e7-c08ea5e1d1d9   bpm             None
    10  baseline_2  gsr_peakrate  0.142616     Phasic blabla  c41da942-837f-4b46-b1e7-c08ea5e1d1d9    au             None
    11  baseline_2      respi_Ti -0.690535  Inspiration time  c41da942-837f-4b46-b1e7-c08ea5e1d1d9     s             None


Note that this new specification can be easily converted to our old feature
format with a pivot operation:

.. code-block:: pycon

   >>> features_wide = features.pivot_table(values='value', index='reference', columns='id')
   >>> print(features_wide)

    id          gsr_peakrate    ppg_HR  respi_Ti
    reference
    baseline_1      0.739373 -0.186326 -0.123698
    baseline_2      0.142616 -0.410132 -0.690535
    task_1          0.934251       NaN  0.653636
    task_2         -0.171955       NaN  0.055566

