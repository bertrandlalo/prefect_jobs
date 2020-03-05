import gc
import logging
import os
import pathlib

import psutil
from prefect import context

from iguazu.core.files import LocalFile, QuetzalFile

logger = logging.getLogger(__name__)


class CustomFileHandler(logging.FileHandler):
    pass


def logging_handler(task, old_state, new_state):
    logger.debug('Managing log due to state change from %s to %s',
                 type(old_state).__name__,
                 type(new_state).__name__)
    context_backend = context.temp_url.backend
    target_path = (
            pathlib.Path('logs') /
            context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
            'RUNNING'
    )
    log_filename = f'{context.task_full_name}-{task.slug}-{context.task_run_count}.log'

    if new_state.is_running() or new_state.is_finished():
        logger.debug('Configuring logs for %s', task)
        # look at backend mode and create adapter with name

        if context_backend == 'quetzal':
            logger.debug('Uploading logs to quetzal')
            file_class = QuetzalFile
            init_kwargs = {'workspace_id': context.temp_url.workspace_id}
        else:
            logger.debug('Uploading logs to local temporary folder')
            file_class = LocalFile
            init_kwargs = {}

        file_adapter = file_class(filename=log_filename, path=target_path, temporary=True, **init_kwargs)

    if new_state.is_running():
        # Configurate Log Formatter and Handler
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)8s - %(name)s.%(funcName)s:%(lineno)s | %(message)s'
        )
        handler = CustomFileHandler(file_adapter.file_str, mode='a')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(handler)

    elif new_state.is_finished():
        state_name = str(type(new_state).__name__).upper()
        # if state_name in ['MAPPED', ]:
        #     return new_state
        logger.debug('Closing logs for %s', task)
        root = logging.getLogger()
        for hdlr in root.handlers[:]:  # Note the copy: we need to modify this list while iterating over it
            # look for the current logging handler
            if not isinstance(hdlr, CustomFileHandler):
                # ignore all other handlers
                continue
            # When found!!
            # Remove handler from root logger
            root.handlers = [hdlr for hdlr in root.handlers if not isinstance(hdlr, CustomFileHandler)]
            # Close the handler, flush all log messages
            hdlr.flush()
            hdlr.close()
            if context_backend == 'local':
                # move from 'RUNNING' folder to final one (given task final status)
                pathlib.Path(file_adapter.file.parents[1] / state_name).mkdir(parents=True, exist_ok=True)
                file_adapter.file.rename(file_adapter.file.parents[1] / state_name / file_adapter.basename)
            else:  # quetzal
                # upload on quetzal
                try:
                    file_adapter.upload()
                    # change path in base metadata and upload them
                    file_adapter.metadata['base']['path'] = str(
                        pathlib.Path(file_adapter.metadata['base']['path']).parents[
                            0] / state_name / file_adapter.basename)
                    file_adapter.upload_metadata()
                except RuntimeError:
                    import ipdb;
                    ipdb.set_trace()
    return new_state


def garbage_collect_handler(task, old_state, new_state):
    # only trigger this when we pass from a non finished to a finished state
    if not old_state.is_finished() and new_state.is_finished():
        logger.debug('Managing garbage collection for %s on change from %s to %s',
                     task.name,
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

                mem_percent = process.memory_percent()
                mem_usage_gb = process.memory_info().rss / (1 << 30)
                logger.info('Memory usage after gc collect: %.2f Gb (%.2f %%)',
                            mem_usage_gb, mem_percent)
        except:
            logger.debug('Failed to garbage collect', exc_info=True)

    return new_state
