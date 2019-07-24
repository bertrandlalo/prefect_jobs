import logging
import os
import tempfile
import uuid

import click
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from prefect.engine.executors import DaskExecutor

from iguazu.cli.flows import str2bool
from iguazu.recipes import execute_flow, registry


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
        secrets=dict(
            SLACK_WEBHOOK_URL=os.environ['SLACK_WEBHOOK_URL'],
        )
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

    # Run the galvanic feature extraction every day at noon
    galvanic_features_flow = registry['galvanic_features']
    galvanic_features_kwargs = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
        limit=50,
        shuffle=True,
    )
    scheduler.add_job(execute_flow,
                      args=(galvanic_features_flow, galvanic_features_kwargs, executor, context_parameters),
                      id=f'galvanic-features-{uuid.uuid4()}', name='galvanic-features',
                      trigger=CronTrigger(hour=12),
                      max_instances=1)

    # Galvanic summarization once a week
    galvanic_summary_flow = registry['summarize_galvanic']
    galvanic_summary_kwags = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
    )
    scheduler.add_job(execute_flow,
                      args=(galvanic_summary_flow, galvanic_summary_kwags, executor, context_parameters),
                      id=f'galvanic-summary-{uuid.uuid4()}', name='galvanic-summary',
                      trigger=CronTrigger(day=7, hour=0),
                      max_instances=1)

    # Run the behavior feature extraction every day at 3 pm
    behavior_features_flow = registry['behavior_features']
    behavior_features_kwargs = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
        limit=50,
        shuffle=True,
    )
    scheduler.add_job(execute_flow,
                      args=(behavior_features_flow, behavior_features_kwargs, executor, context_parameters),
                      id=f'behavior-features-{uuid.uuid4()}', name='behavior-features',
                      trigger=CronTrigger(hour=15),
                      max_instances=1)

    # Behavior summarization once a week
    behavior_summary_flow = registry['summarize_behavior']
    behavior_summary_kwags = dict(
        data_source='quetzal',
        workspace_name=workspace_name,
    )
    scheduler.add_job(execute_flow,
                      args=(behavior_summary_flow, behavior_summary_kwags, executor, context_parameters),
                      id=f'behavior-summary-{uuid.uuid4()}', name='behavior-summary',
                      trigger=CronTrigger(day=7, hour=1),
                      max_instances=1)

    logger.info('Scheduler jobs configured. Running scheduler...')
    scheduler.start()


def _ping_job():
    """No-operation job

    The purpose of this function is to the have APScheduler do something
    regularly
    """
    pass
