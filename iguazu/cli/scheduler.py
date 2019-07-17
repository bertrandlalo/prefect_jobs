import logging
import os
import tempfile
import uuid

import click
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from iguazu.cli.flows import str2bool
from iguazu.recipes import execute_flow, registry
from iguazu.executors import DaskExecutor


logger = logging.getLogger(__name__)


@click.group('scheduler')
def scheduler_group():
    """Iguazu scheduler commands"""
    pass


@scheduler_group.command()
@click.option('--scheduler-address', required=True,
              help='Scheduler address')
def run(scheduler_address):
    """Run the iguazu scheduler"""

    workspace_name = os.environ['IGUAZU_WORKSPACE']

    # Prefect preparations
    executor = DaskExecutor(scheduler_address, name='iguazu-auto')
    context_parameters = dict(
        temp_dir=tempfile.mkdtemp(),
        quetzal_logs_workspace_name=workspace_name,
    )
    quetzal_required_envvars = {'QUETZAL_URL', 'QUETZAL_USER', 'QUETZAL_PASSWORD', 'QUETZAL_INSECURE'}
    if quetzal_required_envvars <= set(os.environ):
        # All of these keys exist in the environment
        quetzal_kws = dict(
            url=os.environ['QUETZAL_URL'],
            username=os.environ['QUETZAL_USER'],
            password=os.environ['QUETZAL_PASSWORD'],
            insecure=str2bool(os.environ['QUETZAL_INSECURE']),
        )
        context_parameters['quetzal_client'] = quetzal_kws
    else:
        logger.warning('Incomplete quetzal environment variables! Some of the '
                       'scheduled flows may fail because of lack of quetzal client. '
                       'Missing variables: %s.', quetzal_required_envvars - set(os.environ))

    # Scheduling
    scheduler = BlockingScheduler()

    # Simple no-op task every minute
    scheduler.add_job(_ping_job, id='ping', name='ping',
                      trigger=IntervalTrigger(minutes=1))

    # Print dataset every 5 min
    print_dataset_flow = registry['print_dataset']
    print_dataset_kwargs = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
    )
    scheduler.add_job(execute_flow,
                      args=(print_dataset_flow, print_dataset_kwargs, executor, context_parameters),
                      id=f'print-dataset-{uuid.uuid4()}', name='print-dataset',
                      trigger=IntervalTrigger(minutes=10),
                      max_instances=1)

    # Run the galvanic feature extraction every hour
    galvanic_features_flow = registry['galvanic_features']
    galvanic_features_kwargs = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
    )
    scheduler.add_job(execute_flow,
                      args=(galvanic_features_flow, galvanic_features_kwargs, executor, context_parameters),
                      id=f'galvanic-features-{uuid.uuid4()}', name='galvanic-features',
                      #trigger=CronTrigger(minute=20))
                      trigger=IntervalTrigger(minutes=2),
                      max_instances=1)
    # trigger=CronTrigger(minute=23))
    #
    # for flow_name in ('print_dataset', 'galvanic_features'):
    #     scheduler.add_job(execute_flow, args=(registry[flow_name], {}, executor, context_parameters),
    #                       id=flow_name, name=flow_name,
    #                       trigger=CronTrigger(minute=57))

    scheduler.start()


def _ping_job():
    """No-operation job

    The purpose of this function is to the have APScheduler do something
    regularly
    """
    pass
