from typing import Optional

import pandas as pd
import prefect

from iguazu.core.exceptions import IguazuError
from iguazu.functions.behavior import extract_space_stress_features
from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import SKIPRESULT
from iguazu.helpers.tasks import get_base_meta, task_upload_result, task_fail


class SpaceStressFeatures(prefect.Task):
    def __init__(self,
                 events_hdf5_key: Optional[str] = None,
                 output_hdf5_key: Optional[str] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.events_hdf5_key = events_hdf5_key
        self.output_hdf5_key = output_hdf5_key
        self.force = force

    def run(self, parent: FileProxy, events: FileProxy, temporary: Optional[bool] = False) -> FileProxy:
        '''
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is to interpret the information computed
        from participant actions and game stimulations to get a score on each wave.
        See the documentation of :func:`behavior.extract_space_stress_scores`.

        Parameters
        ----------
        parent: file proxy with parent events ('unity_events' original stream)
        events:  file proxy with standardized events related to player actions and game stimuations
        temporary: boolean to decide whether or not output file should be temporary

        Returns
        -------
        output: file proxy with

        '''

        output = parent.make_child(suffix='_scores', temporary=temporary)
        self.logger.info('Space Stress scores for %s -> %s', parent, output)

        events_group = self.events_hdf5_key or '/iguazu/events/standard'
        output_group = self.output_hdf5_key or '/iguazu/features/behavior'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        try:
            # check if previous task succeeded
            if events.metadata.get('iguazu', {}).get('state') == 'FAILURE' \
                    or events.metadata.get('iguazu', {}).get('state') == 'FAILURE':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            events_file = events.file
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(events_file, 'r') as store:
                df_events = pd.read_hdf(store, events_group)
                features = extract_space_stress_features(df_events)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state)
                # Manage output, save to file
                task_upload_result(self, features, meta, state, output, output_group)
                self.logger.info('Extract space-stress final scores finished successfully, '
                                 'final dataframe has shape %s', features.shape)
                return output
        except Exception as ex:
            # Manage output, save to file
            self.logger.warning('SpaceStressFeatures failed with an exception', exc_info=True)
            task_fail(self, ex, output, output_group)
