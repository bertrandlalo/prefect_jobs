import logging
import pathlib
import shutil

from prefect import context

logger = logging.getLogger(__name__)


class CustomFileHandler(logging.FileHandler):
    pass


def logging_handler(task, old_state, new_state):
    if new_state.is_running():
        if 'temp_dir' not in context or not context.temp_dir:
            logger.info('Logs cannot be saved without a temp_dir')
            return new_state

        log_filename = (
            pathlib.Path(context.temp_dir) /
            'logs' /
            context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
            f'{context.task_full_name}-{task.slug}'
        ).with_suffix('.log')
        log_filename.parent.mkdir(parents=True, exist_ok=True)
        handler = CustomFileHandler(str(log_filename.resolve()), mode='a')
        handler.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(handler)

    elif new_state.is_finished():
        root = logging.getLogger()
        for hdlr in root.handlers:
            if isinstance(hdlr, CustomFileHandler):
                hdlr.flush()
                hdlr.close()
                final_filename = (
                    pathlib.Path(context.temp_dir) /
                    'logs' /
                    context.scheduled_start_time.strftime('%Y%m%d-%H%M%S') /
                    str(type(new_state).__name__).upper() /
                    f'{context.task_full_name}-{task.slug}'
                ).with_suffix('.log')
                final_filename.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(hdlr.baseFilename, final_filename)
        # Remove handler from root logger
        root.handlers = [hdlr for hdlr in root.handlers if not isinstance(hdlr, CustomFileHandler)]

    return new_state
