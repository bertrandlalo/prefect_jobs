import collections
import enum
import logging
import pathlib
from typing import NoReturn

import numpy as np
import pandas as pd

logger = logging.getLogger()


@enum.unique
class EventSpecificationErrorCode(enum.Enum):
    """Enumeration of known event specification errors"""
    OK = 0
    BAD_TYPE = 1
    BAD_SHAPE = 2
    MISSING_COLUMN = 3
    INCORRECT_COLUMN_TYPE = 4
    INCORRECT_CONTENTS = 5
    REPEATED_ID = 6
    BEGIN_END_ORDER = 7
    ROW_ORDER = 8


@enum.unique
class FeatureSpecificationErrorCode(enum.Enum):
    """Enumeration of known feature specification errors"""
    OK = 0
    BAD_TYPE = 1
    BAD_SHAPE = 2
    MISSING_COLUMN = 3
    INCORRECT_COLUMN_TYPE = 4


@enum.unique
class SignalSpecificationErrorCode(enum.Enum):
    """Enumeration of known signal specification errors"""
    OK = 0
    BAD_TYPE = 1
    BAD_SHAPE = 2
    BAD_SAMPLING = 3
    INCORRECT_COLUMN_TYPE = 4
    UNKNOWN_COLUMN_NAME = 5
    BAD_ANNOTATION_INDEX = 6
    BAD_ANNOTATION_CONTENTS = 7


class SpecificationError(Exception):
    """Exception used when an object does not meet a specification"""

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class EventSpecificationError(SpecificationError):
    """Exception used when an object does not meet the events specification"""
    pass


class FeatureSpecificationError(SpecificationError):
    """Exception used when an object does not meet the features specification"""
    pass


class SignalSpecificationError(SpecificationError):
    """Exception used when an object does not meet the signals specification"""
    pass


def check_event_specification(obj, *, version=None):
    """ Verify that the input conforms to the event specification

    The event specification is detailed on :ref:`event_specs`.

    Parameters
    ----------
    obj: object
        Input object to verify. Usually a dataframe
    version: str
        Specification version. If not set, it uses the latest version.

    Returns
    -------
    None

    Raises
    ------
    EventSpecificationError
        When there is a violation of the specification.

    """

    if version is None:
        version = '1'  # this is the latest version at the moment

    if version == '1':
        _check_event_specification_v1(obj)
    else:
        raise ValueError(f'Unknown event specification version "{version}"')


def _check_event_specification_v1(obj):
    # [implicit] - it must be a dataframe
    if not isinstance(obj, pd.DataFrame):
        raise EventSpecificationError('Events must be a dataframe',
                                      EventSpecificationErrorCode.BAD_TYPE)
    dataframe = obj

    # [1] - dimensions (probably not necessary with dataframes)
    if len(dataframe.shape) != 2:  # pragma: no cover
        raise EventSpecificationError('Dataframe must have two dimensions',
                                      EventSpecificationErrorCode.BAD_SHAPE)

    # [2] - required columns
    required_columns = ('id', 'name', 'begin', 'end', 'data')
    for col in required_columns:
        if col not in dataframe.columns:
            raise EventSpecificationError(f'Missing "{col}" column',
                                          EventSpecificationErrorCode.MISSING_COLUMN)

    # [2] - column types
    object_columns = ('id', 'name', 'data')
    for col in object_columns:
        if dataframe[col].dtype != np.dtype(object):
            raise EventSpecificationError(f'Column "{col}" must be of object dtype',
                                          EventSpecificationErrorCode.INCORRECT_COLUMN_TYPE)

    # Got this pearl from https://stackoverflow.com/a/43191959 to
    # checking if a data series is strings
    if not dataframe['id'].apply(type).eq(str).all():
        raise EventSpecificationError(f'Column "id" must be all strings',
                                      EventSpecificationErrorCode.INCORRECT_CONTENTS)
    if not dataframe['name'].apply(lambda x: isinstance(x, str) or x is None).all():
        raise EventSpecificationError(f'Column "name" must contain strings or None',
                                      EventSpecificationErrorCode.INCORRECT_CONTENTS)

    if not pd.core.dtypes.common.is_datetime64_any_dtype(dataframe['begin']):
        raise EventSpecificationError('Column "begin" must be a timestamp',
                                      EventSpecificationErrorCode.INCORRECT_COLUMN_TYPE)
    if pd.isna(dataframe['begin']).any():
        raise EventSpecificationError('Column "begin" cannot have missing values',
                                      EventSpecificationErrorCode.INCORRECT_CONTENTS)
    if not pd.isna(dataframe['end']).all() and not pd.core.dtypes.common.is_datetime64_any_dtype(dataframe['end']):
        raise EventSpecificationError('Column "end" must be a timestamp',
                                      EventSpecificationErrorCode.INCORRECT_COLUMN_TYPE)
    if not dataframe['data'].apply(lambda x: isinstance(x, dict) or x is None).all():
        raise EventSpecificationError(f'Column "data" must contain dictionaries or None',
                                      EventSpecificationErrorCode.INCORRECT_CONTENTS)

    # [2] uniqueness
    if not dataframe['id'].is_unique:
        raise EventSpecificationError('Column "id" must have unique values',
                                      EventSpecificationErrorCode.REPEATED_ID)

    # [3] begin <= end
    if not np.all(pd.isna(dataframe['end']) | (dataframe['begin'] <= dataframe['end'])):
        raise EventSpecificationError('Column "end" must be larger or equal to column "begin"',
                                      EventSpecificationErrorCode.BEGIN_END_ORDER)

    # [4] order
    argsort_values = sort_standard_events(
        dataframe.assign(number=np.arange(dataframe.shape[0]))
    )['number'].values
    is_sorted = np.all(argsort_values[:-1] < argsort_values[1:])
    if not is_sorted:
        raise EventSpecificationError('Events dataframe must be ordered by "begin", "end", "id"',
                                      EventSpecificationErrorCode.ROW_ORDER)


def empty_events() -> pd.DataFrame:
    """ Create an spec-valid empty events dataframe

    Use this function instead of a simple empty dataframe, since this function
    sets up the correct columns and their types.

    Returns
    -------
    pd.DataFrame
        An empty dataframe with the minimum column and dtype requirements for
        the event specification

    """
    columns = {
        'id': np.dtype('O'),
        'name': np.dtype('O'),
        'begin': np.dtype('datetime64[ns]'),
        'end': np.dtype('datetime64[ns]'),
        'data': np.dtype('O'),
    }
    dataframe = pd.DataFrame(columns=list(columns)).astype(dtype=columns)
    return dataframe


def sort_standard_events(dataframe: pd.DataFrame) -> pd.DataFrame:
    """ Sort an event dataframe according to the specification

    This function returns a copy of the input dataframe with the rows ordered
    by begin timestamp, end timestamp (nans go last) and id.

    You may want to use this function whenever creating specification-correct
    event dataframes, since the validation function uses this same function to
    check the order.

    Parameters
    ----------
    dataframe
        Event dataframe with id, begin and end columns.

    Returns
    -------
    A copy of the dataframe with a different order.

    """
    req_columns = {'id', 'begin', 'end'}
    if req_columns > set(dataframe.columns):
        raise ValueError('Missing required columns to sort events')
    tz = None
    if pd.core.dtypes.common.is_datetime64tz_dtype(dataframe['begin']):
        tz = dataframe['begin'].dtype.tz
    sorted_dataframe = (
        dataframe
            .assign(end_na=lambda x: x['end'].fillna(pd.Timestamp.max.tz_localize(tz=tz)))
            .sort_values(by=['begin', 'end_na', 'id'])
            .drop(columns='end_na')
    )
    return sorted_dataframe


def check_feature_specification(obj, *, version=None):
    """ Verify that the input conforms to the feature specification

    The feature specification is detailed on :ref:`feature_specs`.

    Parameters
    ----------
    obj: object
        Input object to verify. Usually a dataframe
    version: str
        Specification version. If not set, it uses the latest version.

    Returns
    -------
    None

    Raises
    ------
    FeatureSpecificationError
        When there is a violation of the specification.

    """
    if version is None:
        version = '1'  # this is the latest version at the moment

    if version == '1':
        _check_feature_specification_v1(obj)
    else:
        raise ValueError(f'Unknown feature specification version "{version}"')


def _check_feature_specification_v1(obj):
    # [implicit] - it must be a dataframe
    if not isinstance(obj, pd.DataFrame):
        raise FeatureSpecificationError('Features must be a dataframe',
                                        FeatureSpecificationErrorCode.BAD_TYPE)
    dataframe = obj

    # [1] - dimensions (probably not necessary with dataframes)
    if len(dataframe.shape) != 2:  # pragma: no cover
        raise FeatureSpecificationError('Dataframe must have two dimensions',
                                        FeatureSpecificationErrorCode.BAD_SHAPE)

    # [2] - required columns
    required_columns = ('id', 'value', 'reference')
    for col in required_columns:
        if col not in dataframe.columns:
            raise FeatureSpecificationError(f'Missing "{col}" column',
                                            FeatureSpecificationErrorCode.MISSING_COLUMN)

    # [2] - column types
    object_columns = ('id',)
    for col in object_columns:
        if dataframe[col].dtype != np.dtype(object):
            raise FeatureSpecificationError(f'Column "{col}" must be of object dtype',
                                            FeatureSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


def empty_features() -> pd.DataFrame:
    """ Create an spec-valid empty features dataframe

    Use this function instead of a simple empty dataframe, since this function
    sets up the correct columns and their types

    Returns
    -------
    pd.DataFrame
        An empty dataframe with the minimum column and dtype requirements for
        the features specification

    """
    columns = {
        'id': np.dtype('O'),
        'value': np.dtype('O'),
        'reference': np.dtype('O'),
    }
    dataframe = pd.DataFrame(columns=list(columns)).astype(dtype=columns)
    return dataframe


def check_signal_specification(signals_obj, annotations_obj=None, *, version=None):
    """ Verify that the input conforms to the signal specification

    The signal specification is detailed on :ref:`signal_specs`.

    Parameters
    ----------
    signals_obj: object
        Input signals object to verify. As of today (version 1), it can only be
        a dataframe.
    annotations_obj: object
        Optional input annotations object to verify. As of today (version 1),
        it can only be a dataframe
    version: str
        Specification version. If not set, it uses the latest version.

    Returns
    -------
    None

    Raises
    ------
    SignalSpecificationError
        When there is a violation of the specification.

    """
    if version is None:
        version = '1'  # this is the latest version at the moment

    if version == '1':
        _check_signal_specification_v1(signals_obj)
        _check_signal_annotations_specification_v1(signals_obj, annotations_obj)
    else:
        raise ValueError(f'Unknown feature specification version "{version}"')


def _check_signal_specification_v1(obj):
    # [implicit] - it must be a dataframe
    if not isinstance(obj, pd.DataFrame):
        raise SignalSpecificationError('Signals must be a dataframe',
                                       SignalSpecificationErrorCode.BAD_TYPE)
    dataframe = obj

    # [1] - dimensions (probably not necessary with dataframes)
    if len(dataframe.shape) != 2:  # pragma: no cover
        raise SignalSpecificationError('Dataframe must have two dimensions',
                                       SignalSpecificationErrorCode.BAD_SHAPE)

    # [2] - datetime index
    index = dataframe.index
    if not pd.core.dtypes.common.is_datetime64_any_dtype(index):
        raise SignalSpecificationError('Dataframe must have a datetime index',
                                       SignalSpecificationErrorCode.BAD_TYPE)

    # [3] - uniform time support
    # Use dsu.pandas_helpers.estimate_rate, since that code already raises
    # a DSUException on the same cases that we want to test
    if dataframe.shape[0] >= 2:
        from dsu.pandas_helpers import estimate_rate
        from dsu.exceptions import DSUException
        try:
            estimate_rate(dataframe)
        except DSUException as ex:
            raise SignalSpecificationError(f'Invalid dataframe index: {ex}',
                                           SignalSpecificationErrorCode.BAD_SAMPLING) from ex

    # [4] - known columns
    # Use mne channel names for standard 10/05 to avoid writing them down
    from mne.channels import make_standard_montage
    known_columns = (
            make_standard_montage('standard_1005').ch_names +  # EEG
            ['I', 'II', 'III', 'aVR', 'aVL', 'aVF'] +  # ECG
            ['PPG', 'GSR', 'PZT']
    )
    for col in dataframe.columns:
        if col == 'sample_number':
            continue
        if col not in known_columns:
            raise SignalSpecificationError(f'Unexpected "{col}" column',
                                           SignalSpecificationErrorCode.UNKNOWN_COLUMN_NAME)

    # [5] - column types
    for col in known_columns:
        if col not in dataframe.columns:
            continue
        if not np.issubdtype(dataframe[col].dtype, np.number):
            raise SignalSpecificationError(f'Column "{col}" must be of numeric dtype',
                                           SignalSpecificationErrorCode.INCORRECT_COLUMN_TYPE)

    if 'sample_number' in dataframe.columns:
        if not np.issubdtype(dataframe['sample_number'], np.integer):
            raise SignalSpecificationError('Column "sample_number" must be of integer dtype',
                                           SignalSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


def _check_signal_annotations_specification_v1(signals_obj, annotations_obj):
    # Accept None, which means that there are no specifications
    if annotations_obj is None:
        return

    # [implicit] - it must be a dataframe
    if not isinstance(annotations_obj, pd.DataFrame):
        raise SignalSpecificationError('Annotations must be a dataframe',
                                       SignalSpecificationErrorCode.BAD_TYPE)
    # Synonyms for shorter code
    signals = signals_obj
    annotations = annotations_obj

    # Same index
    if not set(annotations.index).issubset(set(signals.index)):
        raise SignalSpecificationError('Annotations does not have the same index of the signals',
                                       SignalSpecificationErrorCode.BAD_ANNOTATION_INDEX)

    # Same columns or subset of columns. No other columns
    if not set(annotations).issubset(set(signals)):
        # Here, since we are using sets, < means "is superset of" (or "not a subset of")
        diff = set(annotations) - set(signals)
        raise SignalSpecificationError(f'Annotations have additional columns not present in signals: '
                                       f'{", ".join(diff)}',
                                       SignalSpecificationErrorCode.UNKNOWN_COLUMN_NAME)

    # String type
    col_is_str = annotations.applymap(type).ne(str).any(axis='index')
    if col_is_str.any():
        raise SignalSpecificationError('Annotations must be all string values',
                                       SignalSpecificationErrorCode.BAD_ANNOTATION_CONTENTS)

    # NaN values on signal have a non-empty annotation
    # TODO: Can't think of a loop-less way to do this at the moment.
    #       The main problem here is that annotationos and signals may have
    #       completely different shapes
    nan_idx, nan_col = np.where(signals.isna().values)
    nan_idx = signals.index[nan_idx]
    nan_col = signals.columns[nan_col]
    for i, j in zip(nan_idx, nan_col):
        if annotations.loc[i, j] == '':
            raise SignalSpecificationError('Annotations on samples where signal is NaN must '
                                           'not be empty',
                                           SignalSpecificationErrorCode.BAD_ANNOTATION_CONTENTS)

    # No NaN or None values. This is redundant with the string type check.
    pass


def empty_signals() -> pd.DataFrame:
    """ Create an spec-valid empty signals dataframe

    Use this function instead of a simple empty dataframe, since this function
    sets up the correct columns and their types

    Returns
    -------
    pd.DataFrame
        An empty dataframe with the minimum column and dtype requirements for
        the signals specification

    """
    columns = {}
    dataframe = pd.DataFrame(columns=list(columns))
    dataframe.index = dataframe.index.astype('datetime64[ns]')
    return dataframe


def infer_standard_groups(hdf_path) -> dict:
    standard_groups = collections.defaultdict(dict)
    with pd.HDFStore(hdf_path, 'r') as store:
        groups = list(store)
        for g in groups:

            if g.endswith('/annotations'):
                logger.debug('Ignoring group %s due to naming', g)
                continue

            # Check signals specs
            try:
                check_signal_specification(pd.read_hdf(store, g))
                logger.debug('Group %s meets the signal specification', g)
                standard_groups.setdefault('signals', [])
                standard_groups['signals'].append(g)
            except SpecificationError as ex:
                logger.debug('Dataframe on HDF5 under key %s is not '
                             'a standard signals dataframe due to  %s',
                             g, ex)

            # Check event specs
            try:
                check_event_specification(pd.read_hdf(store, g))
                logger.debug('Group %s meets the event specification', g)
                standard_groups.setdefault('events', [])
                standard_groups['events'].append(g)
            except SpecificationError as ex:
                logger.debug('Dataframe on HDF5 under key %s is not '
                             'a standard events dataframe due to  %s',
                             g, ex)

            # Check feature specs
            try:
                check_feature_specification(pd.read_hdf(store, g))
                logger.debug('Group %s meets the features specification', g)
                standard_groups.setdefault('features', [])
                standard_groups['features'].append(g)
            except SpecificationError as ex:
                logger.debug('Dataframe on HDF5 under key %s is not '
                             'a standard features dataframe due to  %s',
                             g, ex)
    return standard_groups


def store_output(f: pathlib.Path, key: str, *, dataframe: pd.DataFrame = None,
                 annotations: pd.DataFrame = None) -> NoReturn:
    """ Store dataframe and annotations into a HDF file """
    with pd.HDFStore(str(f.resolve()), 'w') as store:
        if dataframe is not None:
            dataframe.to_hdf(store, key)
        if annotations is not None:
            annotations.to_hdf(store, key + '/annotations')
