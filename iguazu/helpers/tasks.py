from prefect.engine.runner import ENDRUN

from iguazu import __version__ as iguazu_version
from iguazu.helpers.states import GracefulFail


def get_base_meta(task, state=None, **kwargs):
    meta = {
        'source': 'iguazu',
        'task_name': task.__class__.__name__,
        'task_module': task.__class__.__module__,
        'state': state,
        'version': iguazu_version,
    }
    meta.update(kwargs)
    return meta


def graceful_fail(meta, output, state='FAILURE'):
    if meta.get('state', None) == state:
        # Until https://github.com/PrefectHQ/prefect/issues/1163 is fixed,
        # this is the only way to skip with results
        grace = GracefulFail('Task failed but generated empty dataframe', result=output)
        raise ENDRUN(state=grace)
