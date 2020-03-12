import pathlib
import random
import string
import warnings
from datetime import timedelta

import pandas as pd
import pandas.core.common
import pandas.util.testing as tm
import prefect
import pytest
from prefect import Flow
from prefect.engine.signals import ENDRUN
from prefect.engine.state import Finished
from prefect.utilities.debug import raise_on_exception

import iguazu
from iguazu import Task
from iguazu.core.files import LocalFile


def test_unknown_init_kwarg():
    # Test Task constructor keyword arguments:
    # A task with unknown keyword arguments should raise a TypeError
    # when an instance is created. Users should manage their custom keyword
    # arguments before calling the ``super().__init__()`` constructor

    with pytest.raises(TypeError):
        Task(qwertyuiop=True,
             asdfghjkl=1,
             zxcvbn=None)


def test_state_handler_default():

    def handler(*args):
        pass

    t1 = Task(state_handlers=[handler])
    assert t1.state_handlers == [handler]

    t2 = Task()
    assert len(t1.state_handlers) != 0


def test_cache_default():

    def validator(*args):
        pass

    delta = timedelta(hours=1)
    t1 = Task(cache_for=delta)
    assert t1.cache_for == delta

    t2 = Task(cache_validator=validator)
    assert t2.cache_validator == validator

    t3 = Task()
    assert t3.cache_for is not None
    assert t3.cache_validator is not None


class PandasModeSpy(Task):
    """Simple task that returns the current pandas chained_assignment mode"""
    def run(self):
        # Make an operation that triggers a chained_assigment warning
        df = tm.makeDataFrame()
        df2 = df[df.A > 1]
        df2['B'] += 1
        return pd.get_option('mode.chained_assignment')


def test_pandas_context_none(temp_url):
    initial_mode = pd.get_option('mode.chained_assignment')

    with Flow('test_pandas_context_none') as flow:
        task = PandasModeSpy(pandas_chained_assignment=None)
        task()

    with prefect.context(caches={}):
        flow_state = flow.run()
    result = list(flow_state.result.values())[0].result
    assert result is None
    assert pd.get_option('mode.chained_assignment') == initial_mode


def test_pandas_context_warn(temp_url):
    initial_mode = pd.get_option('mode.chained_assignment')

    with Flow('test_pandas_context_warn') as flow:
        task = PandasModeSpy(pandas_chained_assignment='warn')
        task()

    with warnings.catch_warnings(record=True) as w:
        with prefect.context(caches={}):
            flow_state = flow.run()

    # Keep only the SettingWithCopyWarning warnings, there could be others
    w = [_w for _w in w if _w.category == pandas.core.common.SettingWithCopyWarning]
    assert len(w) == 1

    result = list(flow_state.result.values())[0].result
    assert result == 'warn'
    assert pd.get_option('mode.chained_assignment') == initial_mode


def test_pandas_context_raise(temp_url):
    initial_mode = pd.get_option('mode.chained_assignment')

    with Flow('test_pandas_context_error') as flow:
        task = PandasModeSpy(pandas_chained_assignment='raise')
        task()

    with pytest.raises(pandas.core.common.SettingWithCopyError):
        with raise_on_exception(), prefect.context(caches={}):
            flow.run()

    assert pd.get_option('mode.chained_assignment') == initial_mode


def test_pandas_context_other(temp_url):
    initial_mode = pd.get_option('mode.chained_assignment')

    with Flow('test_pandas_context_disable') as flow:
        task = PandasModeSpy(pandas_chained_assignment=False)
        task()

    with prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result
    assert result == initial_mode

    assert pd.get_option('mode.chained_assignment') == initial_mode


class CustomException(Exception):
    pass


class TaskWithException(Task):
    def run(self, *, value):
        if value < 0:
            raise CustomException
        elif value > 0:
            raise ValueError
        return value


def test_graceful_exceptions_fail(temp_url):
    task = TaskWithException(graceful_exceptions=())

    with Flow('test_graceful_exceptions_fail') as flow:
        task(value=-1)

    with raise_on_exception(), prefect.context(caches={}), pytest.raises(CustomException):
        flow.run()


def test_graceful_exceptions_handle_failed(mocker, temp_url):
    graceful_fail_task_method = mocker.patch('iguazu.core.tasks.Task._graceful_fail',
                                             side_effect=[ENDRUN(state=Finished())])
    task = TaskWithException(graceful_exceptions=(CustomException, ))

    with Flow('test_graceful_exceptions_handle_failed') as flow:
        task(value=+1)

    with raise_on_exception(), prefect.context(caches={}), pytest.raises(ValueError):
        flow.run()

    graceful_fail_task_method.assert_not_called()


def test_graceful_exceptions_handle_graceful(mocker, temp_url):
    graceful_fail_task_method = mocker.patch('iguazu.core.tasks.Task._graceful_fail',
                                             side_effect=[ENDRUN(state=Finished())])
    task = TaskWithException(graceful_exceptions=(CustomException, ))

    with Flow('test_graceful_exceptions_handle_graceful') as flow:
        task(value=-1)

    with prefect.context(caches={}):
        flow.run()

    graceful_fail_task_method.assert_called_once()
    call_args = graceful_fail_task_method.call_args[0]
    assert isinstance(call_args[0], CustomException)


def test_bad_graceful_implementation(mocker, temp_url):
    graceful_fail_task_method = mocker.patch('iguazu.core.tasks.Task._graceful_fail',
                                             return_value=['something'])
    task = TaskWithException(graceful_exceptions=(CustomException, ))

    with Flow('test_bad_graceful_implementation') as flow:
        task(value=-1)

    with raise_on_exception(), prefect.context(caches={}), pytest.raises(RuntimeError):
        flow.run()

    graceful_fail_task_method.assert_called_once()


def test_default_outputs(mocker, temp_url):
    return_value = 'hello world'
    default_outputs_method = mocker.patch('iguazu.core.tasks.Task.default_outputs',
                                          return_value=return_value)

    task = TaskWithException(graceful_exceptions=(CustomException, ))

    with Flow('test_default_outputs') as flow:
        task(value=-1)

    with prefect.context(caches={}):
        flow_state = flow.run()

    default_outputs_method.assert_called()

    result = list(flow_state.result.values())[0].result
    assert result == return_value


class TaskWithOutputFile(Task):

    def run(self, *, name, fail=False):
        if fail:
            raise CustomException('Failed by design')
        local_file = self.default_outputs(name=name, fail=fail)
        return local_file

    def default_outputs(self, **inputs):
        local_file = LocalFile(filename=inputs['name'], path='', temporary=True)
        return local_file


@pytest.fixture(scope='function')
def filename():
    return ''.join(random.choices(string.ascii_lowercase, k=6))


def test_default_meta_success(temp_url, filename):
    family = 'unit-tests'
    task = TaskWithOutputFile(metadata_journal_family=family)

    with Flow('test_default_meta_success') as flow:
        task(name=filename)

    with prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result
    meta = result.metadata
    assert family in meta
    assert meta[family]['status'] == 'SUCCESS'
    assert meta[family]['created_by'] == 'iguazu'
    assert meta[family]['task'] == f'{__name__}.TaskWithOutputFile'
    assert meta[family]['version'] == iguazu.__version__
    assert meta[family]['problem'] is None


def test_default_meta_graceful_fail(temp_url, filename):
    family = 'unit-tests'
    task = TaskWithOutputFile(graceful_exceptions=(CustomException,),
                              metadata_journal_family=family)

    with Flow('test_default_meta_graceful_fail') as flow:
        task(name=filename, fail=True)

    with prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result
    meta = result.metadata
    assert family in meta
    assert meta[family]['status'] == 'FAILED'
    assert meta[family]['created_by'] == 'iguazu'
    assert meta[family]['task'] == f'{__name__}.TaskWithOutputFile'
    assert meta[family]['version'] == iguazu.__version__
    assert meta[family]['problem'] == {
        'type': f'{__name__}.CustomException',
        'title': 'Failed by design',
    }


class TaskWithManyOutputFile(Task):

    def run(self, *, name1, name2):
        local_file_1 = LocalFile(
            filename='file1.bin',
            path='',
            temporary=True,
        )
        local_file_2 = LocalFile(
            filename='file2.bin',
            path='',
            temporary=True,
        )
        # tmp_file_1 = self.temp_dir / name1
        # local_file_1 = LocalFile(tmp_file_1, self.temp_dir)
        #
        # tmp_file_2 = self.temp_dir / name1
        # local_file_2 = LocalFile(tmp_file_2, self.temp_dir)

        return local_file_1, local_file_2, 'something else'


def test_default_meta_many_files_success(temp_url, filename):
    family = 'unit-tests'
    task = TaskWithManyOutputFile(metadata_journal_family=family)
    filename1 = filename
    filename2 = filename[::-1]

    with Flow('test_default_meta_many_files_success') as flow:
        task(name1=filename1, name2=filename2)

    with prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result
    assert isinstance(result[0], LocalFile)
    assert isinstance(result[1], LocalFile)
    assert not isinstance(result[2], LocalFile)

    for r in result[:2]:
        meta = r.metadata
        assert family in meta
        assert meta[family]['status'] == 'SUCCESS'
        assert meta[family]['created_by'] == 'iguazu'
        assert meta[family]['task'] == f'{__name__}.TaskWithManyOutputFile'
        assert meta[family]['version'] == iguazu.__version__
        assert meta[family]['problem'] is None


def test_handle_outputs_auto_uploads(mocker, temp_url, filename):
    upload = mocker.patch('iguazu.core.files.local.LocalFile.upload')
    task = TaskWithManyOutputFile()
    filename1 = filename
    filename2 = filename[::-1]

    with Flow('test_auto_upload') as flow:
        task(name1=filename1, name2=filename2)

    with prefect.context(caches={}):
        flow.run()

    assert upload.call_count == 2
