from typing import Optional

import pandas as pd
import prefect

from iguazu.functions.unity import extract_sequences
from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import SKIPRESULT
from iguazu.helpers.tasks import get_base_meta, task_upload_result, task_fail, IguazuError


class ExtractSequences(prefect.Task):

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
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        events_file = events.file.resolve()
        try:
            # check if previous task succeeded
            if events_file.metadata['iguazu']['state'] != 'SUCCESS':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            with pd.HDFStore(events_file, 'r') as events_store:

                # TODO discuss: select column before sending it to a column
                df_events = pd.read_hdf(events_store, events_group)

                df_output = extract_sequences(df_events, self.sequences)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state, bad_ratio=df_output.bad.mean())
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                return output
        except Exception as ex:
            # Manage output, save to file
            task_fail(self, ex, output, output_group)

