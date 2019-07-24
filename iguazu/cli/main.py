import logging

import click
import coloredlogs
import prefect.utilities.logging as prefect_logging

from iguazu.cli.deploy import deploy_group
from iguazu.cli.flows import flows_group
from iguazu.cli.scheduler import scheduler_group


@click.group()
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
              required=False, default=None, help='Python logging level.')
@click.option('--colored-logs', is_flag=True, default=False,
              help='Put colors on the logs')
@click.option('--quetzal-logs', default=None, type=click.STRING,
              required=False, help='Quetzal workspace name to upload logs.')
@click.pass_context
def cli(ctx, log_level, colored_logs, quetzal_logs):
    """Command-line utility for Iguazu operations"""

    # TODO: consider accepting a .yaml or .json file that has a dictConfig

    # Initialize logging for the CLI
    log_level = log_level or logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s %(asctime)s %(name)s %(message)s',
    )
    # Set quetzal workspace logs in click context to provide it to inner commands
    if quetzal_logs and not ctx.resilient_parsing:
        ctx.obj = ctx.obj or {}
        ctx.obj['quetzal_logs'] = quetzal_logs

    if colored_logs:
        try:
            for name in (None, 'prefect'):
                logger = logging.getLogger(name)
                logger.setLevel(log_level)
                field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
                field_styles.pop('levelname', None)
                level_styles = dict(
                    debug=dict(),
                    info=dict(color='green'),
                    warning=dict(color='yellow'),
                    error=dict(color='red'),
                    critical=dict(color='red', bold=coloredlogs.CAN_USE_BOLD_FONT),
                )
                coloredlogs.install(level=log_level, logger=logger, field_styles=field_styles, level_styles=level_styles)
            # Remove stream handler from prefect, because we are using the root handler
            prefect_logging.prefect_logger.handlers = [
                hdlr for hdlr in prefect_logging.prefect_logger.handlers
                if not isinstance(hdlr, logging.StreamHandler)
            ]

        except Exception as ex:
            click.secho(f'Could not setup colored logs: {ex}', fg='yellow')


cli.add_command(deploy_group)
cli.add_command(flows_group)
cli.add_command(scheduler_group)


if __name__ == '__main__':
    cli()
