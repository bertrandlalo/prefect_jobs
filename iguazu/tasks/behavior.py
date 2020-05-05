from typing import Optional

import pandas as pd
import prefect

import iguazu
from iguazu.core.exceptions import SoftPreconditionFailed
from iguazu.core.files import FileAdapter
from iguazu.functions.behavior import extract_space_stress_features
from iguazu.functions.specs import infer_standard_groups
from iguazu.utils import deep_update


class SpaceStressFeatures(iguazu.Task):
    def __init__(self,
                 events_hdf5_key: Optional[str] = None,
                 output_hdf5_key: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.events_hdf5_key = events_hdf5_key
        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self,
            events: pd.DataFrame,
            parent: FileAdapter) -> FileAdapter:
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()

        self.logger.info('Behavior feature extraction for events=%s -> %s',
                         events, output_file)
        features = extract_space_stress_features(events)
        if not features.empty:
            features.loc[:, 'file_id'] = parent.id

        with pd.HDFStore(output_file.file, 'w') as store:
            features.to_hdf(store, self.output_hdf5_key)
        deep_update(output_file.metadata, {'standard': infer_standard_groups(output_file.file_str)})
        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        parent = original_kws['parent']
        output = self.create_file(
            parent=parent,
            suffix=f'_behavior_features',
            temporary=False,
        )
        return output
