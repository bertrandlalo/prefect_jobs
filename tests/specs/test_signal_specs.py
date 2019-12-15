from datetime import datetime, timedelta
import random as rand

import numpy as np
import pandas as pd
import pytest
from mne.channels import make_standard_montage

from iguazu.functions.specs import (
    check_signal_specification, empty_signals,
    SignalSpecificationError, SignalSpecificationErrorCode
)


@pytest.fixture(scope='function')
def random():
    rand.seed(0)
    np.random.seed(0)


@pytest.fixture(scope='function')
def channels():
    eeg_channels = make_standard_montage('standard_1005').ch_names
    ecg_channels = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF']
    other_channels = ['PPG', 'GSR', 'PZT']
    return eeg_channels + ecg_channels + other_channels


@pytest.fixture(scope='function')
def signals(channels, random):
    """A specification-correct signals dataframe"""
    fs = 512
    pandas_freq = f'{int(1e9 / fs)}nS'
    n_samples = fs * 10  # 10 seconds of data
    timestamps = pd.date_range(start=datetime.now(), periods=n_samples, freq=pandas_freq)
    n_channels = len(channels)

    data = np.random.uniform(size=(n_samples * n_channels))
    nan_idx = np.random.choice(np.arange(n_samples * n_channels),
                               size=100, replace=False)
    data[nan_idx] = np.nan
    data = data.reshape(n_samples, n_channels)
    dataframe = pd.DataFrame(data=data,
                             columns=channels,
                             index=timestamps)

    return dataframe


@pytest.fixture(scope='function')
def example_signals_annotations(signals, random):
    """The specification-correct signal example shown in the docs"""
    channel_subset = ['Fp1', 'Fpz', 'Fp2', 'I', 'II', 'III', 'PPG', 'GSR', 'PZT']
    signals = signals[channel_subset].copy()
    annotations = signals.applymap(lambda x: 'unknown' if np.isnan(x) else '')

    # Create some fake artifacts
    idx1 = (signals.index[1:3], ['Fpz', 'Fp1'])
    signals.loc[idx1] = np.nan
    annotations.loc[idx1] = 'electrode pop'

    idx2 = (signals.index[[1, 4, -2, -1]], 'Fp2')
    signals.loc[idx2] = np.nan
    annotations.loc[idx2] = 'saturated'

    idx3 = (signals.index[-3:], ['I', 'II', 'III'])
    signals.loc[idx3] = np.nan
    annotations.loc[idx3] = 'disconnected'

    idx4 = (signals.index[2:4], ['GSR'])
    signals.loc[idx4] = np.nan
    annotations.loc[idx4] = 'saturated'

    # Only select the rows with some annotation
    idx_sparse = signals.isna().any(axis='columns')
    annotations = annotations.loc[idx_sparse].copy()

    return signals, annotations


def test_empty():
    """Test that an empty dataframe is valid

    (As long as the required columns exist!)
    """
    empty = empty_signals()
    check_signal_specification(empty)


def test_unknown_version(signals):
    """Test only the current specification version

    If a new version of the signals specification is implemented, this unit
    test should be updated to the next version.
    """
    with pytest.raises(ValueError):
        # This should fail because version='2' does not exist yet
        check_signal_specification(signals, version='2')


def test_correct_signal_dataframe(signals):
    """Test a correct event dataframe"""
    # This should not raise anything
    check_signal_specification(signals)


def test_correct_signal_example_dataframe(example_signals_annotations):
    """Test that the signal example shown in the docs conforms to the specs"""
    signals, annotations = example_signals_annotations
    check_signal_specification(signals, annotations)


def test_incorrect_type():
    """Test validation error due to incorrect input type"""
    _check_and_assert_raises(dict(), None, SignalSpecificationErrorCode.BAD_TYPE)


def test_bad_shape():
    """Test validation error due to incorrect shape"""
    # I have no idea how to create a N-dimensional dataframe, this might be
    # an useless part of the spec
    pass


def test_missing_column(signals):
    """Test validation error due to missing columns"""
    # No required columns in spec
    pass


def test_unexpected_columns(signals):
    """Test that unknown columns raise a validation error"""
    cols = ('foo', 'bar', 'baz')
    for ch in cols:
        signals = signals.head(n=10).copy()
        signals[ch] = 0
        _check_and_assert_raises(signals, None, SignalSpecificationErrorCode.UNKNOWN_COLUMN_NAME)


def test_column_type(signals, channels):
    """Test validation error due to incorrect column type"""
    columns = signals.columns[:10]
    signals = signals.head(n=10)[columns].copy()
    for ch in columns:
        signals_ch = signals.copy()
        signals_ch[ch] = signals_ch[ch].astype(str)
        _check_and_assert_raises(signals_ch, None, SignalSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


def test_datetime_index(signals):
    """Test validation error when index is not a datetime"""
    signals.index = np.arange(signals.shape[0])
    _check_and_assert_raises(signals, None, SignalSpecificationErrorCode.BAD_TYPE)


def test_non_uniform_sampling(signals, random):
    """Test that non-uniform sampling raises a validation error"""
    random_deltas_ms = np.random.uniform(low=0, high=1000, size=signals.shape[0]).astype('timedelta64[ms]')
    signals.index += random_deltas_ms
    _check_and_assert_raises(signals, None, SignalSpecificationErrorCode.BAD_SAMPLING)


def test_sample_number_integer(signals):
    """Test that sample_number with integer does not fail"""
    signals['sample_number'] = np.arange(signals.shape[0])
    check_signal_specification(signals)


def test_sample_number_non_integer(signals):
    """Test that sample_number with non integer fails"""
    signals['sample_number'] = np.arange(signals.shape[0]).astype(np.float)
    _check_and_assert_raises(signals, None, SignalSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


def test_annotations_dataframe(signals):
    """Test validation error due to incorrect annotation object type"""
    _check_and_assert_raises(signals, dict(), SignalSpecificationErrorCode.BAD_TYPE)


def test_annotations_same_index(example_signals_annotations):
    """Test validation error due to annotations referring incorrect signal index"""
    signals, annotations = example_signals_annotations
    annotations.index = annotations.index + timedelta(hours=1)
    _check_and_assert_raises(signals, annotations, SignalSpecificationErrorCode.BAD_ANNOTATION_INDEX)


def test_annotations_same_columns(example_signals_annotations):
    """Test validation error due to annotations referring incorrect signal columns"""
    signals, annotations = example_signals_annotations
    cols = ('foo', 'bar', 'baz')
    for ch in cols:
        annotations = annotations.copy()
        annotations[ch] = ''
        _check_and_assert_raises(signals, annotations, SignalSpecificationErrorCode.UNKNOWN_COLUMN_NAME)


def test_annotations_all_string(example_signals_annotations):
    """Test validation error due to annotations having a non-string type"""
    signals, annotations = example_signals_annotations
    signals.iat[0, 0] = 0
    weird_values = (1, np.pi, np.nan, None, '')
    for val in weird_values:
        ann = annotations.copy()
        ann.iat[0, 0] = val
        _check_and_assert_raises(signals, ann, SignalSpecificationErrorCode.BAD_ANNOTATION_CONTENTS)


def test_annotations_non_empty_on_nan(signals):
    """Test validation error due to empty annotation"""
    signals.iat[0, 0] = np.nan
    annotations = signals.applymap(lambda x: '')
    _check_and_assert_raises(signals, annotations, SignalSpecificationErrorCode.BAD_ANNOTATION_CONTENTS)


# Function to DRY the tests above
def _check_and_assert_raises(signal_obj, annotation_obj, code):
    with pytest.raises(SignalSpecificationError) as ex_info:
        check_signal_specification(signal_obj, annotation_obj)
    exception = ex_info.value
    assert exception.code == code
