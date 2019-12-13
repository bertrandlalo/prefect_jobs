.. _signal_specs:

====================
Signal specification
====================

========= ==========
Status    ACCEPTED
--------- ----------
Authors   David
--------- ----------
Reviewers Raphaëlle
--------- ----------
Version   1
--------- ----------
Date      2019-12-13
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
``/iguazu/signal/modality/standard``, where ``modality`` is the source
of the data (e.g. *gsr*, *ppg*, *ecg*, *eeg*, etc.).
See the :ref:`signal_names` table for the appropriate group name particle by
modality. However the name ``standard`` can be replaced with any other, more
descriptive name, such as ``clean`` for the case of fully preprocessed signals.

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

* The index timestamp SHOULD include the timezone information. An index without
  timezone information will be assumed to be in UTC. It is not a specification
  error to omit the timezone information, but it is recommended to keep the
  timezone information ot at least to be consistent with the usage of timezone.

Device-dependent remarks
------------------------

* A signal sample with a known problem specific to the device that measured the
  signal MUST be set to ``NaN``. This includes glitches, saturations, etc.
  See the next section on how to represent the details of this information.


Annotations
-----------

The signal dataframe MAY have a *companion* annotation dataframe that
provides details on ``NaN`` samples. This companion dataframe has the
following specifications:

* It MUST have the same index, so that joining with the original signal
  dataframe is trivial.

* It MUST have the same columns or a subset of the columns of the signal
  dataframe, with the same name. It MUST NOT have other columns.

* It MAY ot have all rows present on the signal dataframe. For storage purposes,
  it SHOULD only contain rows where there is an annotation. For this reason,
  not all rows of the signal dataframe may be present on the annotations
  dataframe.

* The contents of a cell in the annotation dataframe MUST be strings.

* When a signal sample has a ``NaN`` value, the annotation dataframe MUST have
  a string with a non-empty, short identifier of the problem. For example,
  ``'saturated'``, ``'disconnected'``, ``'electrode pop'``, etc. If the problem
  is unknown, the annotation value MAY be ``'unknown'``.

* When a signal sample does not have an annotation, its value MUST be ``''``
  (an empty string). It MUST NOT be ``NaN`` or ``None`` in order to keep a
  homogeneous type.

.. For each signal, an accompanying category column with the same name of the
  signal column and a suffix ``_annotations`` SHOULD be used to mark the kind
  of problem encountered for the ``NaN`` sample. These columns MUST be of object
  type and its contents are either string or ``NaN``.


.. _signal_names:

Signal names and units by modality
----------------------------------

* The names of the signals, that is, the dataframe columns, MUST adhere to the
  names shown in the table below (on the **Column names**), depending on the
  data modality. Take care to follow the suggested HDF5 group name particle to
  adhere to the :ref:`hdf5` guidelines (the particle name refers to the ``...``
  part in ``/iguazu/signal/.../standard``).

  ====================== ================================================ ===== ========================
  Modality               Column names                                     Units HDF5 group name particle
  ====================== ================================================ ===== ========================
  Photoplethysmogram     No standard naming yet. Use ``PPG``.             mmHg? ``ppg``
  ---------------------- ------------------------------------------------ ----- ------------------------
  Electrocardiogram      At least one of the leads in `ECG leads`_.       mV    ``ecg``
  ---------------------- ------------------------------------------------ ----- ------------------------
  Galvanic skin response No standard naming yet. Use ``GSR``.             μS    ``gsr``
  ---------------------- ------------------------------------------------ ----- ------------------------
  Electroencephalogram   At least one on the channels in `EEG channels`_. μV    ``eeg``
  ---------------------- ------------------------------------------------ ----- ------------------------
  Respiration            No standard naming yet. Use ``PZT``.             a.u.? ``pzt``
  ---------------------- ------------------------------------------------ ----- ------------------------
  Eyetracker             ?                                                ?     ?
  ---------------------- ------------------------------------------------ ----- ------------------------
  Electrogastrogram      No standard naming yet.                          μV    ``egg``
  ====================== ================================================ ===== ========================

* The value for each signal SHOULD have a value on a particular unit depending
  on the data modality as shown on the table above.


Examples
========

The following dataframes comply with this specification:

.. code-block:: pycon

   >>> print(signals)
                                        Fp1       Fpz       Fp2         I        II       III       PPG       GSR       PZT
    2019-12-13 15:08:10.593720000  0.548814  0.715189  0.602763  0.044612  0.799796  0.076956  0.959433  0.645570  0.035362
    2019-12-13 15:08:10.595673125       NaN       NaN       NaN  0.365100  0.190567  0.019123  0.222864  0.080532  0.085311
    2019-12-13 15:08:10.597626250       NaN       NaN  0.265040  0.853246  0.475325  0.969206  0.256114       NaN  0.232773
    2019-12-13 15:08:10.599579375  0.310629  0.791227  0.715143  0.765070  0.313591  0.365539  0.912151       NaN  0.025190
    2019-12-13 15:08:10.601532500  0.898638  0.537170       NaN  0.384273  0.703407  0.353075  0.958532  0.207513  0.788468
    ...                                 ...       ...       ...       ...       ...       ...       ...       ...       ...
    2019-12-13 15:08:20.583954375  0.109172  0.690440  0.936051  0.620465  0.306744  0.708886  0.353458  0.099618  0.071292
    2019-12-13 15:08:20.585907500  0.789744  0.823636  0.044040  0.087227  0.796727  0.272207  0.421408  0.471078  0.646950
    2019-12-13 15:08:20.587860625  0.083314  0.830159  0.497194       NaN       NaN       NaN  0.582671  0.502512  0.117097
    2019-12-13 15:08:20.589813750  0.651601  0.182138       NaN       NaN       NaN       NaN  0.283973  0.924912  0.537692
    2019-12-13 15:08:20.591766875  0.256217  0.209902       NaN       NaN       NaN       NaN  0.654544  0.135956  0.092303

Note that the annotations dataframe is sparse; it only has the rows that had
a ``NaN`` sample:

.. code-block:: pycon

   >>> print(annotations)
                                             Fp1            Fpz        Fp2             I            II           III PPG        GSR PZT
    2019-12-13 15:08:10.595673125  electrode pop  electrode pop  saturated
    2019-12-13 15:08:10.597626250  electrode pop  electrode pop                                                           saturated
    2019-12-13 15:08:10.599579375                                                                                         saturated
    2019-12-13 15:08:10.601532500                                saturated
    2019-12-13 15:08:20.208954375                                                                            unknown
    2019-12-13 15:08:20.587860625                                           disconnected  disconnected  disconnected
    2019-12-13 15:08:20.589813750                                saturated  disconnected  disconnected  disconnected
    2019-12-13 15:08:20.591766875                                saturated  disconnected  disconnected  disconnected


Pending
=======

The following items are *pending*, that is, undecided at the time of the
creation of this specification:

* No standard naming of columns in photoplethysmogram, galvanic skin response,
  respiration, eyetracker and electrogastrogram.
* Not enough information / experience on eyetracking data to propose any
  guideline on this data.
* Not enough information / experience on several devices to propose a guideline
  on the units of the respiration and ppg units.


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
