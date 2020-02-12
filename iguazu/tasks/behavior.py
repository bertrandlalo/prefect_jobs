from typing import Optional

import pandas as pd
import prefect

from iguazu.core.exceptions import IguazuError
from iguazu.functions.behavior import extract_space_stress_spawns_stimulations, \
    extract_space_stress_participant_actions, extract_space_stress_features
from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import SKIPRESULT
from iguazu.helpers.tasks import get_base_meta, task_upload_result, task_fail


class SpaceStressSpawnsStimulations(prefect.Task):
    def __init__(self,
                 events_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.events_group = events_group
        self.output_group = output_group
        self.force = force

    def run(self, events: FileProxy) -> FileProxy:
        '''
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is deserialize and interpret data related to spawn events.
        See the documentation of :func:`behavior.extract_space_stress_spawns_events`.

        Parameters
        ----------
        events:  file proxy with input events.

        Returns
        -------
        output: file proxy with descriptions of game stimulations

        '''
        output = events.make_child(suffix='_spawns')
        self.logger.info('Space stress spawn events for %s -> %s', events, output)

        events_group = self.events_group or '/unity/events/unity_events'
        output_group = self.output_group or '/behavior/spacestress/stimulations'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        # At that point, we are sure that the previous tasks succeeded and that
        # the output has not yet been generated ()

        events_file = events.file.resolve()

        try:
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(events_file, 'r') as events_store:
                df_events = pd.read_hdf(events_store, events_group)
                df_output = extract_space_stress_spawns_stimulations(df_events)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state)
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                self.logger.info('Extract space-stress spawns stimulations finished successfully, '
                                 'final dataframe has shape %s', df_output.shape)
                return output
        except Exception as ex:
            # Manage output, save to file
            self.logger.warning('SpaceStressSpawnsStimulations failed with an exception', exc_info=True)
            task_fail(self, ex, output, output_group)


class SpaceStressParticipantActions(prefect.Task):
    def __init__(self,
                 events_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.events_group = events_group
        self.output_group = output_group
        self.force = force

    def run(self, events: FileProxy) -> FileProxy:
        '''
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is deserialize and interpret data related to participant actions.
        See the documentation of :func:`behavior.extract_space_stress_participant_actions`.

        Parameters
        ----------
        events:  file proxy with input events.

        Returns
        -------
        output: file proxy with details on participant actions

        '''
        output = events.make_child(suffix='_actions')
        self.logger.info('Space Stress participant actions for %s -> %s', events, output)

        events_group = self.events_group or '/unity/events/unity_events'
        output_group = self.output_group or '/behavior/spacestress/actions'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        events_file = events.file

        try:
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(events_file, 'r') as events_store:
                df_events = pd.read_hdf(events_store, events_group)
                df_output = extract_space_stress_participant_actions(df_events)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state)
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                self.logger.info('Extract space-stress participant actions finished successfully, '
                                 'final dataframe has shape %s', df_output.shape)
                return output
        except Exception as ex:
            # Manage output, save to file
            self.logger.warning('SpaceStressSpawnsParticipantActions failed with an exception', exc_info=True)
            task_fail(self, ex, output, output_group)


class SpaceStressScores(prefect.Task):
    def __init__(self,
                 actions_group: Optional[str] = None,
                 stimulations_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.actions_group = actions_group
        self.stimulations_group = stimulations_group
        self.output_group = output_group
        self.force = force

    def run(self, parent: FileProxy, stimulations: FileProxy, actions: FileProxy) -> FileProxy:
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
        stimulations:  file proxy with events related to game stimuations
        actions: file proxy with events related to participant actions

        Returns
        -------
        output: file proxy with

        '''
        output = parent.make_child(suffix='_scores')
        self.logger.info('Space Stress scores for %s -> %s', parent, output)

        actions_group = self.actions_group or '/behavior/spacestress/actions'
        stimulations_group = self.stimulations_group or '/behavior/spacestress/stimulations'
        output_group = self.output_group or '/behavior/spacestress/scores'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        try:
            # check if previous task succeeded
            if actions.metadata.get('iguazu', {}).get('state') == 'FAILURE' or stimulations.metadata.get('iguazu',
                                                                                                         {}).get(
                'state') == 'FAILURE':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            actions_file = actions.file
            stimulations_file = stimulations.file
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(actions_file, 'r') as actions_store, \
                    pd.HDFStore(stimulations_file, 'r') as stimulations_store:
                df_actions = pd.read_hdf(actions_store, actions_group)
                df_stimulations = pd.read_hdf(stimulations_store, stimulations_group)

                df_output = extract_space_stress_features(df_stimulations, df_actions)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state)
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                self.logger.info('Extract space-stress final scores finished successfully, '
                                 'final dataframe has shape %s', df_output.shape)
                return output
        except Exception as ex:
            # Manage output, save to file
            self.logger.warning('SpaceStressScores failed with an exception', exc_info=True)
            task_fail(self, ex, output, output_group)
