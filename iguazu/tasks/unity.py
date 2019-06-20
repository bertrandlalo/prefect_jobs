from typing import Dict, Optional
import os

from prefect import task
from prefect.engine import signals
import prefect
import pandas as pd

from iguazu.functions.unity import report_sequences
from iguazu.functions.common import path_exists_in_hdf5
from iguazu.helpers.files import FileProxy


class ReportSequences(prefect.Task):

    def __init__(self,
                 events_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 sequences: Optional[list] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.events_group = events_group
        self.output_group = output_group
        self.sequences = sequences
        self.force = force

    def run(self,
            events: FileProxy) -> FileProxy:

        output = events.make_child(suffix='_sequences')
        self.logger.info('Reporting sequences for events=%s -> %s',
                          events, output)

        # Notes on parameter management
        #
        # if I wanted to admit the rewrite of a parameter foo,
        # 1. Add foo to run parameter as an optional parameter with default None
        # 2.a Manage None with `foo = foo or self.foo`
        #
        # If I wanted to admit a global context value of parameter foo
        # 2.b `foo = foo or self.foo or context.get('foo', None)`
        #
        # Finally, if a default value is needed
        # 2.c `foo = foo or self.foo or context.get('foo', 'default_value')`
        #
        # In the following lines, we are not following these ideas yet. Maybe later.
        events_group = self.events_group or '/unity/events/unity_events'
        output_group = self.output_group or '/unity/sequences_report'

        # Our current force detection code
        if not self.force and path_exists_in_hdf5(output.file, output_group):
            # TODO: consider a function that uses a FileProxy, in particular a
            #       QuetzalFile. In this case, we could read the metadata
            #       instead of downloading the file!
            self.logger.info('Output already exists, skipping')
            # raise signals.SKIP('Output already exists', result=output) #  Does not work!
            # TODO: consider a way to raise a skip with results. Currently, the
            #       only way I think this is possible is by making a new signal
            #       that derives from PrefectStateSignal and that uses a new
            #       custom state class as well.
            #       Another solution could be to use a custom state handler
            return output

        events_file = events.file.resolve()

        with pd.HDFStore(events_file, 'r') as events_store:
            try:
                # TODO discuss: select column before sending it to a column
                df_events = pd.read_hdf(events_store, events_group)

                report = report_sequences(df_events, self.sequences)
                meta = {
                    'source': 'iguazu',
                    'task_name': self.__class__.__name__,
                    'task_module': self.__class__.__module__,
                    'state': 'SUCCESS',
                    'version': '0.0',
                }
            except Exception as ex:
                self.logger.warning('Report VR sequences graceful fail: %s', ex)
                report = pd.DataFrame()
                meta = {
                    'source': 'iguazu',
                    'task_name': self.__class__.__name__,
                    'task_module': self.__class__.__module__,
                    'state': 'FAILURE',
                    'version': '0.0',
                    'exception': str(ex),
                }

        # TODO: re-code the failure handling with respect to a task parameter
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        # if fail_mode == 'fail':  ==> raise exception as it arrives

        # Manage output, save to file
        output_file = output.file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.HDFStore(output_file, 'w') as output_store:
            report.to_hdf(output_store, output_group)
            output_store.get_node(output_group)._v_attrs['meta'] = {
                'vr_sequences': meta,
            }

        # Set meta on FileProxy so that Quetzal knows about this metadata
        output.metadata['vr_sequences'].update(meta)
        output.upload()

        return output
