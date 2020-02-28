import logging
from logging.config import dictConfig

import click

from iguazu import __version__
from iguazu.cli.deploy import deploy_group
from iguazu.cli.flows import flows_group


@click.group()
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              required=False, default=None, help='Python logging level (for the console).')
@click.option('--colored-logs', is_flag=True, default=False,
              help='Put colors on the logs')
def cli(log_level, colored_logs):
    """Command-line utility for Iguazu operations"""
    init_logging(log_level, colored_logs)


def init_logging(log_level, colored_logs):
    # Configure using dictConfig
    config = {
        'version': 1,
        'disable_existing_loggers': False,
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
            'iguazu.cache_validators': {
                'level': 'WARNING',
            },
            'matplotlib': {
                'level': 'WARNING',
            },
            'parso': {
                'level': 'WARNING',
            },
            'backoff': {
                'level': 'WARNING',
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

    # capture warnings on the log
    logging.captureWarnings(True)

    root = logging.getLogger()
    root.info(f'Iguazu {__version__} logging initialized')


@cli.command()
def version():
    """Print version and exit"""
    click.echo(f'Iguazu version {__version__}.')


cli.add_command(deploy_group)
cli.add_command(flows_group)


if __name__ == '__main__':
    cli()
