import logging
from logging.config import dictConfig

import click

from iguazu.cli.deploy import deploy_group
from iguazu.cli.flows import flows_group
from iguazu.cli.scheduler import scheduler_group


@click.group()
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              required=False, default=None, help='Python logging level (for the console).')
@click.option('--colored-logs', is_flag=True, default=False,
              help='Put colors on the logs')
@click.option('--quetzal-logs', default=None, type=click.STRING,
              required=False, help='Quetzal workspace name to upload logs.')
@click.pass_context
def cli(ctx, log_level, colored_logs, quetzal_logs):
    """Command-line utility for Iguazu operations"""

    if quetzal_logs and not ctx.resilient_parsing:
        ctx.obj = ctx.obj or {}
        ctx.obj['quetzal_logs'] = quetzal_logs

    # Configure using dictConfig
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)8s - %(name)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)8s - %(name)s.%(funcName)s:%(lineno)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': '[%(asctime)s] '
                          '%(log_color)s%(levelname)8s%(reset)s - '
                          '%(name)s | %(message_log_color)s%(message)s%(reset)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'log_colors': {
                     'DEBUG': 'green',
                     'INFO': 'blue',
                     'WARNING': 'yellow',
                     'ERROR': 'red',
                     'CRITICAL': 'red,bg_white',
                },
                'secondary_log_colors': {
                    'message': {
                        'INFO': 'blue',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    },
                }
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'debug.log',
                'mode': 'a',
                'formatter': 'detailed',
            },
        },
        'loggers': {
            'prefect': {
                'level': 'NOTSET',
                'handlers': [],
            },
            # Use this template to silence a particular library
            # 'some_name': {
            #     'level': 'WARNING',
            # },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        }
    }
    if colored_logs:
        config['handlers']['console']['formatter'] = 'colored'
    if log_level:
        config['handlers']['console']['level'] = log_level
    dictConfig(config)

    # # Remove existing stream handlers that are not disabled by dictConfig
    # for log in ('prefect',):
    #     logger = logging.getLogger(log)
    #     logger.handlers = [hdlr for hdlr in logger.handlers
    #                        if not isinstance(hdlr, logging.StreamHandler)]
    #     logger.setLevel(logging.NOTSET)

    # capture warnings on the log
    logging.captureWarnings(True)

    root = logging.getLogger()
    root.info('Iguazu logging initialized')

    root.debug('debug')
    root.info('info')
    root.warning('warning')


cli.add_command(deploy_group)
cli.add_command(flows_group)
cli.add_command(scheduler_group)


if __name__ == '__main__':
    cli()
