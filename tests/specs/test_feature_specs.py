import itertools
# from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from iguazu.functions.specs import (
    check_feature_specification, empty_features,
    FeatureSpecificationError, FeatureSpecificationErrorCode
)


@pytest.fixture(scope='function')
def features():
    """A specification-correct feature dataframe

    This particular fixture only has the required columns
    """

    ids = ('ppg_HR', 'gsr_peakrate', 'respi_Ti')
    references = ('baseline_1', 'task_1', 'task_2', 'baseline_2')

    dataframe = pd.DataFrame(itertools.product(ids, references),
                             columns=['id', 'reference'])
    nan_idx = [0, 1, 10]
    dataframe['value'] = np.random.uniform(size=dataframe.shape[0])
    dataframe.loc[nan_idx, 'value'] = np.nan
    return dataframe


def test_empty():
    """Test that an empty dataframe is valid

    (As long as the required columns exist!)
    """
    empty = empty_features()
    check_feature_specification(empty)


def test_unknown_version(features):
    """Test only the current specification version

    If a new version of the feature specification is implemented, this unit
    test should be updated to the next version.
    """
    with pytest.raises(ValueError):
        # This should fail because version='2' does not exist yet
        check_feature_specification(features, version='2')


def test_correct_feature_dataframe(features):
    """Test a correct feature dataframe"""
    # This should not raise anything
    check_feature_specification(features)


def test_incorrect_type():
    """Test validation error due to incorrect input type"""
    _check_and_assert_raises(dict(), FeatureSpecificationErrorCode.BAD_TYPE)


def test_bad_shape():
    """Test validation error due to incorrect shape"""
    # I have no idea how to create a N-dimensional dataframe, this might be
    # an useless part of the spec
    pass


@pytest.mark.parametrize('column', ['id', 'value', 'reference'])
def test_missing_column(features, column):
    """Test validation error due to missing columns"""
    features = features.drop(columns=[column])
    _check_and_assert_raises(features, FeatureSpecificationErrorCode.MISSING_COLUMN)


def test_bad_id_type(features):
    """Test that an id column that is not string fails to validate"""
    features['id'] = np.arange(features.shape[0])
    _check_and_assert_raises(features, FeatureSpecificationErrorCode.INCORRECT_COLUMN_TYPE)


def test_column_type(features):
    """Test validation error due to incorrect column type"""
    # The spec does not have a particular item concerning the types.
    pass


# Function to DRY the tests above
def _check_and_assert_raises(obj, code):
    with pytest.raises(FeatureSpecificationError) as ex_info:
        check_feature_specification(obj)
    exception = ex_info.value
    assert exception.code == code
