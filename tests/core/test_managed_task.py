import prefect
import pytest
from prefect import Flow
from prefect.utilities.debug import raise_on_exception

from iguazu.core.tasks import ManagedTask


def test_function_order(mocker):
    manager = mocker.Mock()
    funcs = {
        'contexts': tuple(),
        'prepare_inputs': dict(),
        'handle_outputs': None,
    }
    for name, rv in funcs.items():
        mocked_func = mocker.patch(f'iguazu.core.tasks.ManagedTask.{name}',
                                   return_value=rv)
        manager.attach_mock(mocked_func, name)

    with Flow('test_function_order') as flow:
        instance = ManagedTask()
        instance()

    with raise_on_exception(), prefect.context(caches={}):
        flow.run()

    expected_calls = [
        mocker.call.contexts(),
        mocker.call.prepare_inputs(),
        mocker.call.handle_outputs(None),
    ]
    manager.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize('func', ['contexts',
                                  'prepare_inputs',
                                  'handle_outputs'])
def test_not_implemented(mocker, func):
    funcs = {
        'contexts': tuple(),
        'prepare_inputs': dict(),
        'handle_outputs': None,
    }
    funcs.pop(func)
    for name, rv in funcs.items():
        mocker.patch(f'iguazu.core.tasks.ManagedTask.{name}',
                     return_value=rv)

    with Flow('test_not_implemented') as flow:
        instance = ManagedTask()
        instance()

    with pytest.raises(NotImplementedError):
        with raise_on_exception(), prefect.context(caches={}):
            flow.run()
