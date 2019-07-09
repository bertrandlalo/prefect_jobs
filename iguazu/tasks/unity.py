from typing import Optional

import pandas as pd
import prefect
from prefect.engine.runner import ENDRUN

from iguazu.functions.common import path_exists_in_hdf5
from iguazu.functions.unity import report_sequences
from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import SkippedResult, GracefulFail


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

            # Until https://github.com/PrefectHQ/prefect/issues/1163 is fixed,
            # this is the only way to skip with results
            skip = SkippedResult('Output already exists, skipping', result=output)
            raise ENDRUN(state=skip)

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
        with pd.HDFStore(output_file, 'w') as output_store:
            report.to_hdf(output_store, output_group)
        # Set meta on FileProxy so that Quetzal knows about this metadata
        output.metadata['task'][self.__class__.__name__] = meta
        output.upload()

        if meta.get('state', None) == 'FAILURE':
            # Until https://github.com/PrefectHQ/prefect/issues/1163 is fixed,
            # this is the only way to skip with results
            grace = GracefulFail('Task failed but generated empty dataframe', result=output)
            raise ENDRUN(state=grace)

        return output
