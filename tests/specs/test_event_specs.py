import itertools
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from iguazu.functions.specs import (
    check_event_specification, empty_events,
    EventSpecificationError, EventSpecificationErrorCode
)


@pytest.fixture(scope='function')
def events():
    """A specification-correct event dataframe"""
    now = datetime.now()
    dataframe = pd.DataFrame({
        'id': [
            'protocol',
            'baseline_1',
            'annotation_1',
            'task_1',
            'artifact_1',
            'artifact_2',
            'task_2',
            'baseline_2',
            'order_test_1',
            'order_test_2',
        ],
        'name': [
            'protocol',
            'baseline',
            'annotation',
            'task',
            'artifact',
            'artifact',
            'task',
            'baseline',
            'order',
            'order',
        ],
        'begin': [
            now,  # 'protocol',
            now + timedelta(seconds=10),  # 'baseline_1',
            now + timedelta(seconds=11),  # 'annotation_1',
            now + timedelta(seconds=20),  # 'task_1',
            now + timedelta(seconds=21),  # 'artifact_1',
            now + timedelta(seconds=25),  # 'artifact_2',
            now + timedelta(seconds=30),  # 'task_2',
            now + timedelta(seconds=60),  # 'baseline_2'
            now + timedelta(seconds=90),  # 'order_test_1'
            now + timedelta(seconds=90),  # 'order_test_2'
        ],
        'end': [
            now + timedelta(seconds=90),  # 'protocol',
            now + timedelta(seconds=20),  # 'baseline_1',
            None,  # 'annotation_1',
            now + timedelta(seconds=30),  # 'task_1',
            None,  # 'artifact_1',
            None,  # 'artifact_2',
            now + timedelta(seconds=30),  # 'task_2',
            now + timedelta(seconds=90),  # 'baseline_2'
            now + timedelta(seconds=91),  # 'order_test_1'
            None,                         # 'order_test_2'
        ],
        'data': [
            {'foo': 'bar'},
            None,
            {'note': 'operator says hi'},
            {'kind': 'eyes-opened'},
            {'kind': 'blink'},
            {},
            {'kind': 'n-back', 'n': 10},
            None,
            None,
            None,
        ],
        'parents': [
            None,
            None,
            None,
            None,
            ['task_1'],
            ['task_1'],
            None,
            None,
            None,
            None,
        ],
        'extra': [
            1, 1, 2, 2, 1, 1, 0, 0, 0, 0,
        ]
    })
    dataframe.index = dataframe.begin
    dataframe.index.name = 'index'
    return dataframe


def test_empty():
    """Test that an empty dataframe is valid

    (As long as the required columns exist!)
    """
    empty = empty_events()
    check_event_specification(empty)


def test_unknown_version(events):
    """Test only the current specification version

    If a new version of the events specification is implemented, this unit
    test should be updated to the next version.
    """
    with pytest.raises(ValueError):
        # This should fail because version='2' does not exist yet
        check_event_specification(events, version='2')


def test_correct_event_dataframe(events):
    """Test a correct event dataframe"""
    # This should not raise anything
    check_event_specification(events)


def test_incorrect_type():
    """Test validation error due to incorrect input type"""
    _check_and_assert_raises(dict(), EventSpecificationErrorCode.BAD_TYPE)


def test_bad_shape():
    """Test validation error due to incorrect shape"""
    # I have no idea how to create a N-dimensional dataframe, this might be
    # an useless part of the spec
    pass


@pytest.mark.parametrize('column', ['id', 'name', 'begin', 'end', 'data'])
def test_missing_column(events, column):
    """Test validation error due to missing columns"""
    events = events.drop(columns=[column])
    _check_and_assert_raises(events, EventSpecificationErrorCode.MISSING_COLUMN)


@pytest.mark.parametrize('column', ['id', 'name', 'data'])
def test_column_type(events, column):
    """Test validation error due to incorrect column type"""
    events[column] = np.random.uniform(size=events.shape[0])
    _check_and_assert_raises(events, EventSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


@pytest.mark.parametrize('column', ['id', 'name'])
def test_non_string_contents(events, column):
    """Test validation error due to non-string id or name"""
    events.at[events.index[0], column] = dict()
    _check_and_assert_raises(events, EventSpecificationErrorCode.INCORRECT_CONTENTS)


@pytest.mark.parametrize('column', ['begin', 'end'])
def test_non_timestamp_contents(events, column):
    """Test validation error due to non-timestamp contents"""
    events[column] = np.random.uniform(size=events.shape[0])
    _check_and_assert_raises(events, EventSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


@pytest.mark.parametrize('tz', ['UTC', 'Europe/Paris', None])
def test_datetime_contents(events, tz):
    """Test that datetime64 and datetime64 with utc are accepted"""
    # Note: tz=None gives a regular datetime64
    events['begin'] = events['begin'].dt.tz_localize(tz=tz)
    events['end'] = events['end'].dt.tz_localize(tz=tz)
    check_event_specification(events)


def test_missing_begin(events):
    """Test validation error due to missing begin"""
    events.loc[events.index[0], 'begin'] = None
    _check_and_assert_raises(events, EventSpecificationErrorCode.INCORRECT_CONTENTS)


@pytest.mark.parametrize('bad_example', [
        [], list, 3, 3.14, 'string', lambda x: x, type('anon', (), {}),
    ])
def test_data_contents(events, bad_example):
    """Test validation error due to invalid data contents"""
    events.at[events.index[0], 'data'] = bad_example
    _check_and_assert_raises(events, EventSpecificationErrorCode.INCORRECT_CONTENTS)


def test_id_uniqueness(events):
    """Test validation error due to duplicated id"""
    events.at[events.index[1], 'id'] = events.at[events.index[0], 'id']
    _check_and_assert_raises(events, EventSpecificationErrorCode.REPEATED_ID)


def test_begin_end_order(events):
    """Test validation error due to end before begin"""
    events['end'] = events['begin'] - timedelta(seconds=1)
    _check_and_assert_raises(events, EventSpecificationErrorCode.BEGIN_END_ORDER)


def test_row_order(events):
    """Test validation error due to incorrect order"""
    small_events = events.head(n=5).reset_index(drop=True)
    index = small_events.index

    # Test all possible row orders (n!), which for n=5 is: n! = 120
    # except the first one; the correct one
    for i, idx in enumerate(itertools.permutations(index)):
        # The first permutation is the correct one
        if i == 0:
            continue
        idx = list(idx)
        reordered = small_events.loc[idx].copy()
        _check_and_assert_raises(reordered, EventSpecificationErrorCode.ROW_ORDER)


def test_row_order_with_nans(events):
    """Test validation error due to incorrect order on particular with NaT"""
    small_events = events.tail(n=5).reset_index(drop=True)
    index = small_events.index

    # Test all possible row orders (n!), which for n=5 is: n! = 120
    # except the first one; the correct one
    for i, idx in enumerate(itertools.permutations(index)):
        # The first permutation is the correct one
        if i == 0:
            continue
        idx = list(idx)
        reordered = small_events.loc[idx].copy()
        _check_and_assert_raises(reordered, EventSpecificationErrorCode.ROW_ORDER)


# Function to DRY the tests above
def _check_and_assert_raises(obj, code):
    with pytest.raises(EventSpecificationError) as ex_info:
        check_event_specification(obj)
    exception = ex_info.value
    assert exception.code == code
