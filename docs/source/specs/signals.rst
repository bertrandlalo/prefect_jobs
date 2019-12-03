.. _signal_specs:

====================
Signal specification
====================

========= ==========
Status    PROPOSAL
--------- ----------
Authors   David
--------- ----------
Reviewers
--------- ----------
Version   0
--------- ----------
Date      2019-10-24
========= ==========

This specification aims to standardize how *signals* are represented so that
pipelines can expect a well-defined structure and properties independently of
any problem or particularities that are protocol or device specific.

Notation
========

For the purposes of a specification, the words MUST, SHOULD, MAY and their
negations are used according to the `RFC-2119`_. In other words, they represent
elements that are an absolute requirement (MUST), a recommendation (SHOULD)
or optional (MAY).

Signal and sample
-----------------

In general, a *signal* is a vector of information; a variable whose value
changes over time.
In the context of digital signal processing, these signals are digital, that is,
the time domain and value range are limited to discrete values.

For the purposes
of Iguazu, a signal is a set of real values, associated to distinct time
instants. Each pair of time and value is denoted a sample. However, for
multivariate signals, it is easier to consider a sample as all the values
associated to a time instant.

Scope
=====

Depending on the device or software that generates or measures signals, there
is often a heterogeneity on how these signals are represented.
The multi-modality nature of our data complicates even further this problem.
Some examples of these heterogeneities:

* Data representation differences:

  * Timeflux uses timestamp indexed :py:class:`pandas.DataFrame` to represent
    signals, but also accepts xarrays.

  * LSL (and by extension, their XDF files) use arrays of float values with
    accompanying timestamps as float values representing seconds.

  * MNE uses their own Raw object, with an underlying :py:class:`numpy.ndarray`
    representation.

  * OpenViBE use a EBML format to save and transmit streams, with a particular
    representation for signals that include their sampling frequency.

* Time differences:

  * Timeflux makes no assumption on the regularity of the signals it handles
    in order to keep any jitter on the time difference between two samples or
    any drift of the device clock.

  * Unprocessed LSL data keep their jitter; timestamps are not necessarily
    regular intervals, especially between chunks of data.

  * Some drivers set the timestamp according to their sampling rate, keeping
    regular intervals, but possibly incurring in a time drift.

  * OpenViBE does not have timestamps but sample numbers. Jitters and drifts
    are handled on the data generation side.

* Device differences:

  * Many devices give the GSR on resistance values, but other devices use
    conductance values.

  * Signal saturation is device-dependent.

While these differences are an unavoidable fact of our datasets, from the
signal-processing point of view:

* Many algorithms rely on equally spaced samples (filtering, DFT, resampling,
  etc.).

* Many standard algorithm implementations work on NumPy arrays, e.g.
  :py:mod:`scipy.signal`.

* NumPy arrays have a homogeneous type (one cannot mix floats and string, for
  example). Pandas allows different types per column, but is limited to 2D
  arrays. Xarrays allows multidimensional datasets with heterogeneous types,
  but we have little experience on its usage at the moment.

These heterogeneities complicate the design and implementation of reusable
pipelines. Therefore, the **scope** of this document is to provide a
standardized representation of signals so that any downstream task can simplify
its code. The specification will address the three sources of heterogeneity
mentioned above: data representation, time and device.

Specification
=============

Representation
--------------

Following the :ref:`Guidelines` concerning :ref:`rule_file_format`,
the preferred format to save standardized Iguazu signals is a
:py:class:`pandas.DataFrame` embedded in a HDF5 file under a key as defined
in the :ref:`hdf5`. The preferred HDF5 key for  is
``/iguazu/signal/modality/prepared``, where ``modality`` is the source
of the data (e.g. *gsr*, *ppg*, *ecg*, *eeg*, etc.).
See the :ref:`signal_names` table for the appropriate group name particle by
modality.

The contents of the dataframe depend on the modality.
However, there are some common elements as described next.

* It MUST have exactly two dimensions. Rows represent *samples*. Columns
  represent *signals*.

* It MUST have an index of type `datetime64[ns]`_ or
  :py:class:`pandas.Timestamp` that represents the time instant of each sample.
  This index MUST represent a time stamp on a nanosecond scale. There are more
  requirements concerning this index on the :ref:`time_support` section.

* Signals on the dataframe MUST have a numeric type, preferrably a
  ``np.float64``. They can be ``NaN``.

* The dataframe MAY have a column named *sample_number*. When present, it MUST
  be of an integer type, it MUST be monotonically increasing and it MUST NOT be
  ``None``.

.. _time_support:

Time support
------------

* The index SHOULD be equally spaced. If it is not exactly equally spaced,
  the difference between two consecutive samples MUST NOT be larger than the
  sampling period (the inverse of the sampling rate).
  Any processing algorithm can assume that the signal samples are equally
  spaced.


Device-dependent remarks
------------------------

* A signal sample with a known problem specific to the device that measured the
  signal MUST be set to ``NaN``. This includes glitches, saturations, etc.

* For each signal, an accompanying category column with the same name of the
  signal column and a suffix ``_annotations`` SHOULD be used to mark the kind
  of problem encountered for the ``NaN`` sample. These columns MUST be of object
  type and its contents are either string or ``NaN``.


.. _signal_names:

Signal names and units by modality
----------------------------------

* The names of the signals, that is, the dataframe columns, MUST adhere to the
  following names, depending on the data modality:

  ====================== ================================= ================================================ =====
  Modality               HDF5 group name particle          Column names                                     Units
  ====================== ================================= ================================================ =====
  Photoplethysmogram     ``ppg``                           No standard naming yet. Use ``ppg``.             mmHg?
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Electrocardiogram      ``ecg``                           At least one of the leads in `ECG leads`_.       mV
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Galvanic skin response ``gsr``                           No standard naming yet. Use ``gsr``.             μS
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Electroencephalogram   ``eeg``                           At least one on the channels in `EEG channels`_. μV
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Respiration            ``respi``                         No standard naming yet. Use ``respi``.           a.u.?
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Eyetracker             ?                                 ?                                                ?
  ---------------------- --------------------------------- ------------------------------------------------ -----
  Electrogastrogram      ``egg``                           No standard naming yet.                          μV
  ====================== ================================= ================================================ =====

* The value for each signal SHOULD have a value on a particular unit depending
  on the data modality as shown on the table above.


Examples
========

The following dataframe conforms to this specification:

.. code-block:: pycon

   >>> print(signals)
                                        Fp1       Fpz       Fp2     respi       gsr       ppg         I Fp1_annotations respi_annotations gsr_annotations
    2019-11-25 18:17:53.559697000       NaN  0.176707  0.134151  0.079310  0.862250  0.064041  0.974728   electrode pop               NaN       saturated
    2019-11-25 18:17:53.561650125  0.270147  0.170591  0.113841  0.140351  0.671598  0.728501  0.345092             NaN               NaN       saturated
    2019-11-25 18:17:53.563603250       NaN  0.137015  0.611275  0.899663  0.078138  0.464530  0.599594   electrode pop               NaN       saturated
    2019-11-25 18:17:53.565556375  0.719263  0.664449  0.583317  0.451203  0.819860  0.900557  0.501669             NaN               NaN       saturated
    2019-11-25 18:17:53.567509500  0.789224  0.741264  0.177518  0.366314  0.734846  0.428777  0.214244             NaN               NaN       saturated
    ...                                 ...       ...       ...       ...       ...       ...       ...             ...               ...             ...
    2019-11-25 18:18:03.549931375  0.594742  0.974215  0.769306  0.882719  0.421463  0.363691  0.349184             NaN      disconnected             NaN
    2019-11-25 18:18:03.551884500  0.282889  0.267101  0.111317  0.087229  0.963758  0.318535  0.226392             NaN      disconnected             NaN
    2019-11-25 18:18:03.553837625       NaN  0.754553  0.762995  0.463562  0.160009  0.717667  0.992356   electrode pop      disconnected             NaN
    2019-11-25 18:18:03.555790750  0.239632  0.487637  0.329782  0.983357  0.032569  0.631128  0.156964             NaN      disconnected             NaN
    2019-11-25 18:18:03.557743875  0.269476  0.935528  0.832609  0.366474  0.292679  0.531649  0.680871             NaN      disconnected             NaN

Appendix
========

ECG leads
---------

There are 12 standard ECG leads:

* Bipolar limb leads I, II and III.
* Augmented unipolar leads aVR, aVL and aVF.
* Unipolar chest leads V1, V2, V3, V4, V5 and V6.

The names of the ECG columns mentioned in :ref:`signal_names` section must be
``I``, ``II``, ``III``,
``aVR``, ``aVL``, ``aVF``,
``V1``, ``V2``, ``V3``, ``V4``, ``V5``, ``V6``,
respectively.

Some useful links concerning ECG leads:

* `Standard 12 lead ECG <https://ecg.utah.edu/lesson/1>`_.
* `Einthoven's triangle <https://en.wikipedia.org/wiki/Einthoven%27s_triangle>`_.


EEG channels
------------

EEG channels must be named according to the `10/20 system`_. If a finer spatial
resolution is needed, a 10/10 or `10/5 system`_ may be used.
For example: ``Fpz``, ``F1``, ``F3``, ``Cz``, etc.


.. _RFC-2119: https://www.ietf.org/rfc/rfc2119.txt
.. _datetime64[ns]: https://docs.scipy.org/doc/numpy/reference/arrays.datetime.html
.. _10/20 system: https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG)
.. _10/5 system: https://doi.org/10.1016/j.neuroimage.2006.09.024
