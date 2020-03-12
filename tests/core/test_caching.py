import prefect
from prefect import Flow
from prefect.utilities.debug import raise_on_exception

from iguazu import Task


# Some notes on the cache:
# On a task, when force is True, the parametrized validator must return a
# cache miss as soon as possible. It does not make sense to verify the cache
# inside the task.run method, because this will not even be called if there is
# a hit on the prefect's cache. This is tested on test_forced_with_prefect_cache
#
# On the other hand, when the task's force is False, prefect may have a cached
# entry with the previous results and it would be useful to use it if present.
# This is tested on test_not_forced_with_prefect_cache
#
# When there is a cached entry, but the tasks' name is in the 'forced_tasks'
# entry of the current prefect context, then the cache should be ignored.
# This is tested on test_forced_from_context


def test_forced_with_prefect_cache(mocker, temp_url):
    # Test that even the prefect cache does not prevent a forced task
    run_method = mocker.patch('iguazu.Task.run',
                              side_effect=['result1', 'result2'])
    task = Task(force=True)

    with Flow('test_forced_with_prefect_cache') as flow:
        task()

    with prefect.context(caches={}):
        flow_state1 = flow.run(run_on_schedule=True)
        cache = prefect.context.caches

    result1 = list(flow_state1.result.values())[0].result

    with prefect.context(caches=cache):  # Note: cache is from previous run
        flow_state2 = flow.run(run_on_schedule=True)

    result2 = list(flow_state2.result.values())[0].result

    assert result1 == 'result1'
    assert result2 == 'result2'
    assert run_method.call_count == 2


def test_not_forced_with_prefect_cache(mocker, temp_url):
    # Test that the prefect cache is used when force=False
    run_method = mocker.patch('iguazu.Task.run',
                              side_effect=['result1', Exception('should not be called')])
    task = Task(force=False)

    with Flow('test_not_forced_with_prefect_cache') as flow:
        task()

    with prefect.context(caches={}):
        flow_state1 = flow.run(run_on_schedule=True)
        cache = prefect.context.caches

    result1 = list(flow_state1.result.values())[0].result

    with raise_on_exception(), prefect.context(caches=cache):  # Note: cache is from previous run
        flow_state2 = flow.run(run_on_schedule=True)

    result2 = list(flow_state2.result.values())[0].result

    assert result1 == 'result1'
    assert result2 == 'result1'
    assert run_method.call_count == 1


def test_forced_from_context(mocker, temp_url):
    # Test that tasks can be forced through a prefect context variable
    run_method = mocker.patch('iguazu.Task.run',
                              side_effect=['result1', 'result2'])
    task = Task(name='foobar', force=False)

    with Flow('test_forced_from_context') as flow:
        task()

    with prefect.context(caches={}):
        flow_state1 = flow.run(run_on_schedule=True)

    result1 = list(flow_state1.result.values())[0].result

    # Note: empty caches, otherwise the prefect cache will hit before the task run
    with prefect.context(caches={}, forced_tasks=['foobar']):
        flow_state2 = flow.run(run_on_schedule=True)

    result2 = list(flow_state2.result.values())[0].result

    assert result1 == 'result1'
    assert result2 == 'result2'
    assert run_method.call_count == 2
