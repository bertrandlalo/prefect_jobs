import logging

import click

from iguazu.cli.deploy import deploy_group
from iguazu.cli.flows import flows_group
from iguazu.cli.scheduler import scheduler_group


@click.group()
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              required=False, default=None, help='Python logging level.')
@click.option('--quetzal-logs', default=None, type=click.STRING,
              required=False, help='Quetzal workspace name to upload logs.')
@click.pass_context
def cli(ctx, log_level, quetzal_logs):
    """Command-line utility for Iguazu operations"""

    # TODO: consider accepting a .yaml or .json file that has a dictConfig

    # Initialize logging for the CLI
    logging.basicConfig(
        level=log_level or logging.WARNING,
        format='%(levelname)s %(asctime)s %(name)s %(message)s',
    )

    # Initialize or rewrite prefect logging
    if log_level is not None:
        import prefect.utilities.logging as prefect_logging
        prefect_logging.prefect_logger.setLevel(log_level)

    # Set quetzal workspace logs in click context to provide it to inner commands
    if quetzal_logs and not ctx.resilient_parsing:
        ctx.obj = ctx.obj or {}
        ctx.obj['quetzal_logs'] = quetzal_logs


cli.add_command(deploy_group)
cli.add_command(flows_group)
cli.add_command(scheduler_group)


if __name__ == '__main__':
    cli()
