import pandas as pd
import pandas.util.testing as tm
import pytest
import prefect
from prefect import Flow
from prefect.utilities.debug import raise_on_exception

from iguazu import Task
from iguazu.core.files import LocalFile, LocalURL


class BadTask(Task):
    def __init__(self,
                 input_one_key='/foo',
                 **kwargs):
        self.auto_manage_input_dataframe('input_one', input_one_key)
        super().__init__(**kwargs)


def test_auto_manage_input_bad_init_order():
    with pytest.raises(AttributeError):
        BadTask()


class TaskWithInputDataFrame(Task):

    def __init__(self,
                 input_one_key='/foo',
                 **kwargs):
        super().__init__(**kwargs)

        self.auto_manage_input_dataframe('input_one', input_one_key)

    def run(self, *, input_one):
        df_result = input_one.mean()
        return df_result


class TaskWithTwoInputDataFrames(Task):

    def __init__(self,
                 input_one_key='/foo',
                 input_two_key='/bar',
                 **kwargs):
        super().__init__(**kwargs)

        self.auto_manage_input_dataframe('input_one', input_one_key)
        self.auto_manage_input_dataframe('input_two', input_two_key)

    def run(self, *, input_one, input_two, offset):
        df_result = input_one.mean() + input_two.mean() + offset
        return df_result


@pytest.fixture(scope='function')
def local_file(tmpdir):
    filename = 'dataframe.hdf5'
    path = tmpdir / filename
    foo = tm.makeDataFrame()
    bar = tm.makeDataFrame()

    with pd.HDFStore(path, 'w') as store:
        foo.to_hdf(store, '/foo')
        bar.to_hdf(store, '/bar')

    url = LocalURL(path=tmpdir)
    with prefect.context(temp_url=url):
        yield LocalFile(filename=filename, path='', temporary=True)


def test_auto_manage_dataframe_default(local_file):
    task = TaskWithInputDataFrame()

    with Flow('test_auto_manage_dataframe_default') as flow:
        file = prefect.Parameter('local_file', default=local_file)
        task(input_one=file)

    with raise_on_exception(), prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result

    df_foo = pd.read_hdf(local_file.file, '/foo')
    assert isinstance(df_foo, pd.DataFrame)

    tm.assert_equal(result, df_foo.mean())


def test_auto_manage_dataframe_init_overwrite(local_file):
    task = TaskWithInputDataFrame(input_one_key='/bar')

    with Flow('test_auto_manage_dataframe_init_overwrite') as flow:
        file = prefect.Parameter('local_file', default=local_file)
        task(input_one=file)

    with raise_on_exception(), prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result

    df_bar = pd.read_hdf(local_file.file, '/bar')
    assert isinstance(df_bar, pd.DataFrame)

    tm.assert_equal(result, df_bar.mean())


def test_auto_manage_dataframe_default_string(local_file):
    task = TaskWithInputDataFrame()
    filename = local_file.file.resolve()

    with Flow('test_auto_manage_dataframe_default_string') as flow:
        file = prefect.Parameter('local_file', default=filename)
        task(input_one=file)

    with raise_on_exception(), prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result

    df_foo = pd.read_hdf(local_file.file, '/foo')
    assert isinstance(df_foo, pd.DataFrame)

    tm.assert_equal(result, df_foo.mean())


def test_auto_manage_dataframe_incorrect_type(local_file, caplog):
    task = TaskWithInputDataFrame()

    with Flow('test_auto_manage_dataframe_default_string') as flow:
        file = prefect.Parameter('local_file', default=123456)
        task(input_one=file)

    with pytest.raises(ValueError), caplog.at_level('FATAL', logger='prefect'):
        with raise_on_exception(), prefect.context(caches={}):
            flow.run()


def test_auto_manage_dataframe_many_inputs(local_file):
    task = TaskWithTwoInputDataFrames()

    with Flow('test_auto_manage_dataframe_many_inputs') as flow:
        file = prefect.Parameter('local_file', default=local_file)
        task(input_one=file, input_two=file, offset=1.23)

    with raise_on_exception(), prefect.context(caches={}):
        flow_state = flow.run()

    result = list(flow_state.result.values())[0].result

    df_foo = pd.read_hdf(local_file.file, '/foo')
    df_bar = pd.read_hdf(local_file.file, '/bar')
    assert isinstance(df_foo, pd.DataFrame)
    assert isinstance(df_bar, pd.DataFrame)

    tm.assert_equal(result, df_foo.mean() + df_bar.mean() + 1.23)
