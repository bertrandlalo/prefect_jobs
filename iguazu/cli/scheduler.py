import datetime
import tempfile
import uuid

import click
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


from iguazu.recipes import execute_flow, registry
from iguazu.executors import DaskExecutor


@click.group('scheduler')
def scheduler_group():
    """Iguazu scheduler commands"""
    pass


@scheduler_group.command()
@click.option('--scheduler-address', required=True,
              help='Scheduler address')
def run(scheduler_address):
    """Run the iguazu scheduler"""
    scheduler = BlockingScheduler()

    executor = DaskExecutor(scheduler_address, name='iguazu-auto')
    context_parameters = dict(
        temp_dir=tempfile.mkdtemp(),
    )

    # Print hello every minute
    scheduler.add_job(hello, id='hello', name='hello', trigger=IntervalTrigger(minutes=1))

    # Print dataset every 5 min
    print_dataset_flow = registry['print_dataset']
    print_dataset_kwargs = dict(
        data_source='local',
        basedir='/Users/david/data/DATA_OMI/raw_hdf5',
    )
    scheduler.add_job(execute_flow,
                      args=(print_dataset_flow, print_dataset_kwargs, executor, context_parameters),
                      id=f'print-dataset-{uuid.uuid4()}', name='print-dataset',
                      trigger=IntervalTrigger(minutes=5))

    # Run the galvanic feature extraction every hour
    galvanic_features_flow = registry['galvanic_features']
    galvanic_features_kwargs = dict(
        data_source='local',
        basedir='/Users/david/data/DATA_OMI/raw_hdf5',
    )
    scheduler.add_job(execute_flow,
                      args=(galvanic_features_flow, galvanic_features_kwargs, executor, context_parameters),
                      id=f'galvanic-features-{uuid.uuid4()}', name='galvanic-features',
                      trigger=CronTrigger(minute=55))
    # trigger=CronTrigger(minute=23))
    #
    # for flow_name in ('print_dataset', 'galvanic_features'):
    #     scheduler.add_job(execute_flow, args=(registry[flow_name], {}, executor, context_parameters),
    #                       id=flow_name, name=flow_name,
    #                       trigger=CronTrigger(minute=57))

    scheduler.start()


def hello():
    print('Hello world at', datetime.datetime.now())
