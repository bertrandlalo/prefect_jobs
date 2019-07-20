import gc
import logging
import os
import pathlib
import tempfile
import shutil

import psutil
from prefect import context
from quetzal.client import helpers

logger = logging.getLogger(__name__)


class CustomFileHandler(logging.FileHandler):
    pass


def logging_handler(task, old_state, new_state):
    logger.debug('Managing log due to state change from %s to %s',
                 type(old_state).__name__,
                 type(new_state).__name__)
    state_name = str(type(new_state).__name__).upper()

    if new_state.is_running():
        logger.debug('Configuring logs for task')
        temp_dir = context.get('temp_dir', None)
        temp_dir = temp_dir or tempfile.mkstemp(prefix=context.task_full_name, suffix='.log')[1]
        log_filename = (
            pathlib.Path(temp_dir) /
            'logs' /
            context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
            state_name /
            f'{context.task_full_name}-{task.slug}-{context.task_run_count}'
        ).with_suffix('.log')
        log_filename.parent.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s %(message)s')
        handler = CustomFileHandler(str(log_filename.resolve()), mode='a')
        handler.setFormatter(formatter)
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
            if 'quetzal_client' in context and 'quetzal_logs_workspace_name' is not None:
                try:
                    logger.debug('Uploading logs to quetzal')
                    client = helpers.get_client(**context.quetzal_client)
                    workspace_details = helpers.workspace.details(client, name=context.quetzal_logs_workspace_name)
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

            # Move to final directory on temp_dir with the state name
            if 'temp_dir' in context:
                log_filename = (
                        pathlib.Path(context.temp_dir) /
                        'logs' /
                        context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
                        state_name /
                        f'{context.task_full_name}-{task.slug}-{context.task_run_count}'
                ).with_suffix('.log')
                log_filename.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(hdlr.baseFilename, log_filename)
                # Clear the parent directory when empty, in a "ask for forgiveness"
                # instead of getting permission
                try:
                    log_filename.parent.rmdir()
                except:
                    # It was not empty
                    pass

    return new_state


def garbage_collect_handler(task, old_state, new_state):

    # only trigger this when we pass from a non finished to a finished state
    if not old_state.is_finished() and new_state.is_finished():
        logger.debug('Managing garbage collection on change from %s to %s',
                     type(old_state).__name__,
                     type(new_state).__name__)
        try:
            process = psutil.Process(os.getpid())
            mem_percent = process.memory_percent()
            mem_usage_gb = process.memory_info().rss / (1 << 30)
            logger.debug('Memory usage is %.2f Gb (%.2f %%)', mem_usage_gb, mem_percent)
            if mem_usage_gb > 2 or mem_percent >= 75:  # usage over 75%
                logger.info('Calling gc, usage was over the limit')
                gc.collect()
        except:
            logger.debug('Failed to garbage collect', exc_info=True)

    return new_state
