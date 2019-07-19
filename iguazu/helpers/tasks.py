import pandas as pd
from prefect.engine.runner import ENDRUN

from iguazu import __version__ as iguazu_version
from iguazu.helpers.states import GracefulFail, GRACEFULFAIL, SKIPRESULT


class IguazuError(Exception):
    pass


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


def task_fail(task, ex, output, output_group, mode='grace'):
    state = 'FAILURE'
    if mode in ('grace', 'skip'):
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        meta = get_base_meta(task, state=state, exception=str(ex))
        # Update iguazu metadata with the current task
        output.metadata['iguazu'].update({task.name: meta, 'state': state})
        task_upload_result(task, pd.DataFrame(), meta, state, output, output_group)
        if mode == 'grace':
            grace = GracefulFail(ex, result=output)
            raise GRACEFULFAIL(state=grace)
        else:  # mode == 'skip':
            raise SKIPRESULT(ex)
    else:  # mode == 'fail'
        # if fail_mode == 'fail':  ==> raise exception as it arrives
        raise ENDRUN


def task_upload_result(task, data, meta, state, output, output_group):
    # Manage output, save to file
    output_file = output.file
    with pd.HDFStore(output_file, 'w') as output_store:
        data.to_hdf(output_store, output_group)
    # Update iguazu metadata with the current task
    output.metadata['iguazu'].update({task.name: meta, 'state': state})
    output.upload()
