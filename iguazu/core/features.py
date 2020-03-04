"""Helper functions for feature generation"""

import pandas as pd

from dataclasses import asdict, fields, is_dataclass


def dataclass_meta_to_dataframe(instance) -> pd.DataFrame:
    """ Transform a dataclass instance field metadata to a pandas dataframe

    Given a dataclass defined as follows::

        @dataclass
        class Thing:
            feature_1 : int = 0
            feature_2 : float = 3.14
            feature_3 : float = field(default=42, metadata=dict(foo='bar'))

    This function will take an instance of this class, such as
    ``Thing(feature_1=1, feature_2=2, feature_3=3)``, and convert it to a
    two-level dictionary where the first level is the field name and the
    second level contains each field's metadata::

        {
            "feature_1": {
            },
            "feature_2": {
            },
            "feature_3": {
                "value": 1,
                "foo": "bar"
            }
        }

    Then, this dictionary is transformed to a
    :py:class:`pandas.DataFrame` using :py:meth:`pandas.DataFrame.from_dict`::

        instance = Thing(feature_1=1, feature_2=2, feature_3=3)
        d = dataclass_meta_to_dataframe(instance)
        dataframe = pd.Dataframe.from_dict(d, orient='index')

    giving::

                   foo
        feature_1  NaN
        feature_2  NaN
        feature_3  bar

    Parameters
    ----------
    instance
        A dataclass instance

    Returns
    -------
    pandas.DataFrame
        A dataframe representation of the dataclass whose index is the field
        name and columns are the field metadata

    """
    if not is_dataclass(instance):
        raise ValueError('Input must be a dataclass')
    d = {}
    for f in fields(instance):
        d[f.name] = f.metadata
    return pd.DataFrame.from_dict(d, orient='index')


def dataclass_to_dataframe(instance) -> pd.DataFrame:
    """ Transform a dataclass instance to a pandas dataframe

    This function creates a dataframe from a dataclass instance, where each
    row is a field of the dataclass. It contains at least one column called
    `value` with the dataclass field value, and as many columns as the metadata
    fields. See :py:func:`dataclass_meta_to_dataframe` on how the metadata of
    a field is extracted.

    Given a dataclass defined as follows::

        @dataclass
        class Thing:
            feature_1 : int = 0
            feature_2 : float = 3.14
            feature_3 : float = field(default=42, metadata=dict(foo='bar'))

    This function will take an instance of this class, such as
    ``Thing(feature_1=1, feature_2=2, feature_3=3)``, and convert it to a
    dataframe that has both value and metadata as follows::

                   value  foo
        feature_1      1  NaN
        feature_2      2  NaN
        feature_3      3  bar

    Parameters
    ----------
    instance
        A dataclass instance

    Returns
    -------
    pandas.DataFrame
        A dataframe representation of the dataclass whose index is the field
        name and columns are both the field value and the field metadata

    """
    if not is_dataclass(instance):
        raise ValueError('Input must be a dataclass')

    value = pd.DataFrame.from_dict(asdict(instance), orient='index', columns=['value'])
    metas = dataclass_meta_to_dataframe(instance)

    dataframe = pd.merge(value, metas, left_index=True, right_index=True)
    return dataframe
