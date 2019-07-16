import logging

import click

from iguazu.cli.deploy import deploy_group
from iguazu.cli.flows import flows_group


@click.group()
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              required=False, default=None, help='Python logging level.')
def cli(log_level):
    """Command-line utility for Iguazu operations"""

    # TODO: consider accepting a .yaml or .json file that has a dictConfig

    # Initialize logging for the CLI
    logging.basicConfig(
        level=log_level or logging.NOTSET,
        format='%(levelname)s %(asctime)s %(name)s %(message)s',
    )

    # Initialize or rewrite prefect logging
    if log_level is not None:
        import prefect.utilities.logging as prefect_logging
        prefect_logging.prefect_logger.setLevel(log_level)


cli.add_command(deploy_group)
cli.add_command(flows_group)


if __name__ == '__main__':
    cli()
