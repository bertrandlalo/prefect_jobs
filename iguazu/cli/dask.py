# Script needed for a custom startup using the --reload option in dask-worker
# See docs: https://docs.dask.org/en/latest/setup/custom-startup.html

import click


@click.command()
def dask_setup(*args, **kwargs):  # This *has* to be named dask_setup
    """Call initialization functions needed for dask"""
    import logging
    import quetzal.client
    from iguazu.cli.main import init_logging

    init_logging(logging.DEBUG, False)
    logger = logging.getLogger(__name__)
    logger.info('Imported quetzal.client %s', quetzal.client.__version__)
    logger.info('Dask preload code ran successfully')
