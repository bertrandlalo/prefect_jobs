import logging
import pathlib
import tempfile

from prefect import context
from quetzal.client import helpers

logger = logging.getLogger(__name__)


class CustomFileHandler(logging.FileHandler):
    pass


def logging_handler(task, old_state, new_state):
    if new_state.is_running():
        temp_dir = context.get('temp_dir', None) or tempfile.mkstemp(prefix=context.task_full_name, suffix='.log')[1]
        log_filename = (
            pathlib.Path(temp_dir) /
            'logs' /
            context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
            f'{context.task_full_name}-{task.slug}-{context.task_run_count}'
        ).with_suffix('.log')
        log_filename.parent.mkdir(parents=True, exist_ok=True)
        handler = CustomFileHandler(str(log_filename.resolve()), mode='a')
        handler.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(handler)

    elif new_state.is_finished():
        root = logging.getLogger()
        for hdlr in root.handlers[:]:  # Note the copy: we need to modify this list while iterating over it
            if not isinstance(hdlr, CustomFileHandler):
                # ignore all other handlers
                continue

            # Remove handler from root logger
            root.handlers = [hdlr for hdlr in root.handlers if not isinstance(hdlr, CustomFileHandler)]

            # Close the handler, flush all log messages
            hdlr.flush()
            hdlr.close()

            # Upload to quetzal if the context information has all the necessary information
            if 'quetzal_client' in context and 'workspace_name' in context:
                try:
                    client = helpers.get_client(**context.quetzal_client)
                    workspace_details = helpers.workspace.details(client, name=context.workspace_name)
                    state_name = str(type(new_state).__name__).upper()
                    target_path = (
                        pathlib.Path('logs') /
                        context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
                        state_name
                    )
                    with open(hdlr.baseFilename, 'rb') as fd:
                        helpers.workspace.upload(client, workspace_details.id, fd,
                                                 path=str(target_path), temporary=True)
                except:
                    # Catch any error, log it and keep going
                    logger.warning('Could not upload logs to quetzal', exc_info=True)

    return new_state
