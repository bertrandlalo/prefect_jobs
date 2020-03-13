""" Tasks related to VR survey features """

import logging

import pandas as pd
import prefect

import iguazu
from iguazu.core.exceptions import (
    PostconditionFailed, SoftPreconditionFailed
)
from iguazu.core.files import FileAdapter
from iguazu.functions.specs import (
    check_feature_specification
)
from iguazu.functions.specs import infer_standard_groups
from iguazu.functions.surveys import extract_report_features, extract_meta_features
from iguazu.utils import deep_update

logger = logging.getLogger(__name__)

meta_survey_config = dict(  # todo: find a way to version this?
    stress_gestion=['space-stress-0-0',
                    'space-stress-1-0',
                    'space-stress-0-2',
                    'space-stress-1-2',
                    'space-stress-0-4',
                    'space-stress-1-4',
                    'cardiac-coherence-1-4',
                    ],
    concentration=['space-stress-0-5',
                   'space-stress-1-5',
                   'cardiac-coherence-1-2',
                   'physio-sonification-0-1',
                   ],
    self_efficacity=['space-stress-0-2',
                     'space-stress-1-2',
                     'space-stress-0-6',
                     'space-stress-1-6',
                     ],
    reactivity=['cardiac-coherence-1-4',
                ],
    interoception=['physio-sonification-0-0',
                   'physio-sonification-0-2',
                   'physio-sonification-0-3'
                   ]
)


class ExtractReportFeatures(iguazu.Task):
    """Extract survey report from standardized events from VR protocol
    """

    def __init__(self, *,
                 events_hdf5_key: str = '/iguazu/events/standard',
                 output_hdf5_key: str = '/iguazu/features/survey_report',
                 temporary_output: bool = False,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.temporary_output = temporary_output
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, events: pd.DataFrame) -> FileAdapter:

        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()
        dataframe = extract_report_features(events)
        self.logger.debug('Obtained %d survey/report features', dataframe.shape[0])
        if not dataframe.empty:
            self.logger.debug('Small extract of survey/report:\n%s',
                              dataframe.to_string(max_rows=5))

        with pd.HDFStore(output_file.file, 'w') as store:
            dataframe.to_hdf(store, self.output_hdf5_key)
        return output_file

    def default_outputs(self, **kwargs):
        """ Survey report default outputs
        """
        original_kws = prefect.context.run_kwargs
        events = original_kws['events']
        # output = events.make_child(suffix='_standard_events')
        output = self.create_file(
            parent=events,
            suffix='_survey_report',
            temporary=self.temporary_output
        )
        return output

    def postconditions(self, results):
        """ Check standard event postconditions

        The postconditions of this task is that the result follows the event
        specification standard.
        """
        super().postconditions(results)

        if not isinstance(results, FileAdapter):
            raise PostconditionFailed('Output was not a file')

        # Postcondition: file is empty
        if results.empty:
            return

        key = self.output_hdf5_key
        with pd.HDFStore(results.file, 'r') as store:
            dataframe = pd.read_hdf(store, key)
            check_feature_specification(dataframe)


class ExtractMetaFeatures(iguazu.Task):
    """Extract survey meta feature from standardized events from VR protocol
    """

    def __init__(self, *,
                 features_hdf5_key: str = '/iguazu/features/survey_report',
                 output_hdf5_key: str = '/iguazu/features/survey_meta',
                 temporary_output: bool = False,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.temporary_output = temporary_output
        self.auto_manage_input_dataframe('features', features_hdf5_key)

    def run(self, features: pd.DataFrame,
            parent: FileAdapter) -> FileAdapter:

        if features.empty:
            raise SoftPreconditionFailed('Input features are empty')

        output_file = self.default_outputs()
        features = extract_meta_features(features, config=meta_survey_config)
        if not features.empty:
            features.loc[:, 'file_id'] = parent.id
        self.logger.debug('Obtained %d survey/meta features', features.shape[0])

        with pd.HDFStore(output_file.file, 'w') as store:
            features.to_hdf(store, self.output_hdf5_key)
        deep_update(output_file.metadata, {'standard': infer_standard_groups(output_file.file_str)})
        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        parent = original_kws['parent']
        output = self.create_file(
            parent=parent,
            suffix=f'_survey_meta',
            temporary=False,
        )
        return output
