.. _event_specs:

=================================
Event and sequences specification
=================================

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

This specification aims to standardize how *events* and *sequences* are
represented so that any function or task that uses *events* or *sequences* can
expect them to follow the structure described in this document. Consequently,
any function or task that generates *events* or *sequences*, regardless of the
data source, should adhere to this specification.

Notation
========

For the purposes of a specification, the words MUST, SHOULD, MAY and their
negations are used according to the `RFC-2119`_. In other words, they represent
elements that are an absolute requirement (MUST), a recommendation (SHOULD)
or optional (MAY).

Time marker
-----------

Throughout this document, all references to *time markers* refer to a timestamp.
The resolution of this timestamp depends on the application.

Events
------

In a broad sense, an event is *something that happens,especially when it is
important* (paraphrased from the Collins dictionary).
On the content of Iguazu and the data that it processes, an
event is a specific point in time (a time marker), with some data associated
to it.

In constrast to regular time series, events are sparse, they seldom occur at
regular intervals.

Events MUST have a timestamp associated to it and an identifier.
More data MAY be associated to it, such as duration, or end marker, and a set
of unstructured data elements.

.. note::

  Although there are frameworks to systematically define events and their
  hierarchy, like the `HED`_ tags project,
  **we are not using HED at the moment**.
  However, HED tags can easily be included on this specification by adding at
  least one additional column to the dataframe Contents_
  described later on this document.

Sequences
---------

Sequences are a specific type of event: it MUST have both a *begin* and an
*end* time marker.

.. note::

  The name *sequence* is a bit odd: it does not refer to a set of ordered
  elements (which is the normal meaning of a *sequence*). The appropriate name
  would be a *segment*. However, it has been historically named *sequence*.

Scope
=====

The problem with events is that their representation is heterogeneous;
most applications, protocols, frameworks and studies represent them in a
different way. For example:

* Open Mind's VR application (before February 2018) used events sent by Unity,
  represented as a timestamp and an identifier. These identifiers are documented
  internally.
* Open Mind's VR protocol (after February 2018) has events sent by Unity,
  represented as a timestamp, a label, a data object and an optional `HED`_ tag.
  These labels are
  `documented internally <https://docs.google.com/spreadsheets/d/1i5c8ZubMFxwV6JB19NoMo1-FmlV79vjQxG4q-plt_Ms/edit#gid=2054745703>`_.
* Most of our Timeflux_ applications (if not all) use events as timestamps with
  a label and a data object.
* LSL_ seem to denote events as *markers*; they have a timestamp and a type.
  I could not find a specification for these markers or types.
* OpenViBE_ defines stimulations as a date, identifier and duration
  (which is usually zero), with an accompanying fixed table of around 400
  `standardized identifiers <http://openvibe.inria.fr/stimulation-codes/>`_.
* In general, real-time applications prefer to send two separate *begin* and
  *end* events, specially when the *end* marker is not known in advance.

The **scope** of this document is to provide a standardized specification for
these events according to Iguazu, so that any task that needs to use these
events can assume that they come in this standard format. It is the
responsiblity of some upstream task to convert from whatever
application-specific format to the Iguazu standard event format.


Specification
=============


Storage
-------

Following the :ref:`Guidelines` concerning :ref:`rule_file_format`,
the preferred format to save standard Iguazu events or sequences is a
:py:class:`pandas.DataFrame` embedded in a HDF5 file under a key as defined
in the :ref:`hdf5`. The preferred HDF5 key for standardized events is
``/iguazu/events/standard``.

Contents
--------

The standardized events dataframe is defined as follows:

#. It MUST have exactly two dimensions.

#. It MUST have the following columns:

   * A column named *id* of type object with string contents. The contents of
     each row for this column MUST be unique and MUST NOT be ``None``.

   * A column named *name* of type object and string contents. The contents of
     each row for this column is not defined by this specification, it is
     reserved for interoperation with other event identification systems or
     external applications. Its value is optional; it MAY be ``None``.

   * A column named *begin*, of type `datetime64[ns]`_ or
     :py:class:`pandas.Timestamp`.  The contents MUST NOT be `NaT`_ or ``None``.

   * A column named *end*, of of type `datetime64[ns]`_ or
     :py:class:`pandas.Timestamp`. This column can be `NaT`_, representing
     events that do not have an ending time marker.

   * A column named *data* of object type. Its contents MUST be either Python
     dictionaries convertible to JSON, or it can be ``None``.

#. For each row, the *end* value MUST be larger or equal than the *begin* value.
   `NaT`_ values are considered as infinity.

#. Its rows MUST be ordered by their *begin* timestamp, with ties resolved by
   their *end* timestamp and finally by their *id*. `NaT`_ values have the
   same order as infinity; they go last (this only applies to the *end* column).

#. It MAY have an index, as long as it meets the order requirements.

#. To meet the uniqueness requirement of the *id* column, this column
   MAY use a notation for repeated events (events with the same *name*) such as
   ``"event_1"``, ``"event_2"``, ... ``"event_N"``, according to their row order.


Examples
========

The following dataframe **does not** conform to this specification, but it is
a likely scenario of data generated by timeflux, biosig or others:

.. code-block:: pycon

    >>> print(raw_events)
                                         label                          data
    2019-10-22 15:08:59.986288  begin-protocol                {'foo': 'bar'}
    2019-10-22 15:09:09.986288  begin-baseline                          None
    2019-10-22 15:09:10.986288      annotation  {'note': 'operator says hi'}
    2019-10-22 15:09:19.986288    end-baseline                          None
    2019-10-22 15:09:19.986288      begin-task       {'kind': 'eyes-opened'}
    2019-10-22 15:09:20.986288        artifact             {'kind': 'blink'}
    2019-10-22 15:09:24.986288        artifact                            {}
    2019-10-22 15:09:29.986288        end-task                          None
    2019-10-22 15:09:29.986288      begin-task   {'kind': 'n-back', 'n': 10}
    2019-10-22 15:09:29.986288        end-task                          None
    2019-10-22 15:09:59.986288  begin-baseline                          None
    2019-10-22 15:10:29.986288    end-baseline                          None
    2019-10-22 15:10:29.986288    end-protocol                          None


The following dataframe is **does** conform to this specification:

.. code-block:: pycon

    >>> print(standard_events)
                                          id        name                      begin                        end                          data   parents  extra
    index
    2019-10-22 15:08:59.986288      protocol    protocol 2019-10-22 15:08:59.986288 2019-10-22 15:10:29.986288                {'foo': 'bar'}      None      1
    2019-10-22 15:09:09.986288    baseline_1    baseline 2019-10-22 15:09:09.986288 2019-10-22 15:09:19.986288                          None      None      1
    2019-10-22 15:09:10.986288  annotation_1  annotation 2019-10-22 15:09:10.986288                        NaT  {'note': 'operator says hi'}      None      2
    2019-10-22 15:09:19.986288        task_1        task 2019-10-22 15:09:19.986288 2019-10-22 15:09:29.986288       {'kind': 'eyes-opened'}      None      2
    2019-10-22 15:09:20.986288    artifact_1    artifact 2019-10-22 15:09:20.986288                        NaT             {'kind': 'blink'}  [task_1]      1
    2019-10-22 15:09:24.986288    artifact_2    artifact 2019-10-22 15:09:24.986288                        NaT                            {}  [task_1]      1
    2019-10-22 15:09:29.986288        task_2        task 2019-10-22 15:09:29.986288 2019-10-22 15:09:29.986288   {'kind': 'n-back', 'n': 10}      None      0
    2019-10-22 15:09:59.986288    baseline_2    baseline 2019-10-22 15:09:59.986288 2019-10-22 15:10:29.986288                          None      None      0

The associated types of the dataframe above are:

.. code-block:: pycon

   >>> print(standard_events.dtypes)
    id                 object
    name               object
    begin      datetime64[ns]
    end        datetime64[ns]
    data               object
    parents            object
    extra               int64
    dtype: object


.. _HED: http://www.hedtags.org/
.. _OpenViBE: http://openvibe.inria.fr/stream-structures/
.. _LSL: https://github.com/sccn/labstreaminglayer
.. _Timeflux: https://timeflux.io
.. _datetime64[ns]: https://docs.scipy.org/doc/numpy/reference/arrays.datetime.html
.. _NaT: https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html#datetimes
.. _RFC-2119: https://www.ietf.org/rfc/rfc2119.txt
