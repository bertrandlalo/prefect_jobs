import datetime
import itertools
import logging

from iguazu import __version__
from iguazu.cache_validators import ParametrizedValidator
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import LoadDataframe, MergeDataframes, SlackTask
from iguazu.tasks.galvanic import CleanGSRSignal, ApplyCVX, DetectSCRPeaks, Downsample, ExtractGSRFeatures

logger = logging.getLogger(__name__)


class GalvanicFeaturesFlow(PreparedFlow):
    """Extract all  cardiac features from a file dataset"""

    REGISTRY_NAME = 'features_galvanic'
    DEFAULT_QUERY = f"""
        SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
               base->>'filename' AS filename,  -- this is just to help the human debugging this
               omi->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
               iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
        FROM   metadata
        WHERE  base->>'state' = 'READY'                -- No temporary files
        AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
        AND    (standard->'standardized')::bool        -- Only standardized files
        AND    standard->'groups' ? '/iguazu/signal/gsr/standard' -- containing the GSR signal
        AND    standard->'groups' ? '/iguazu/events/standard'     -- containing standardized events
        AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
     --   AND    iguazu->>'version' <= '{__version__}'   -- by this iguazu version or earlier
        ORDER BY id                                -- always in the same order
    """

    def _build(self, *, plot=False, **kwargs):
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omi=None,
            standard=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families

        # When the query is set by kwargs, leave the query and dialect as they
        # come. Otherwise, set to the default defined just above
        if not kwargs.get('query', None):
            kwargs['query'] = self.DEFAULT_QUERY
            kwargs['dialect'] = 'postgres_json'

        # The cardiac features flow requires an upstream dataset flow in order
        # to provide the input files. Create one and deduce the tasks to
        # plug the cardiac flow to the output of the dataset flow
        dataset_flow = GenericDatasetFlow(**kwargs)
        raw_signals = dataset_flow.terminal_tasks().pop()
        events = raw_signals
        self.update(dataset_flow)

        # Instantiate tasks
        clean = CleanGSRSignal(
            signals_hdf5_key='/iguazu/signal/gsr/standard',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/signal/gsr/clean',
        )
        downsample = Downsample(
            signals_hdf5_key='/iguazu/signal/gsr/clean',
            output_hdf5_key='/iguazu/signal/gsr/downsampled',
        )
        cvx = ApplyCVX(
            signals_hdf5_key='/iguazu/signal/gsr/downsampled',
            output_hdf5_key='/iguazu/signal/gsr/cvx',
        )
        scrpeaks = DetectSCRPeaks(
            signals_hdf5_key='/iguazu/signal/gsr/cvx',
            output_hdf5_key='/iguazu/signal/gsr/scrpeaks',
        )

        extract_features = ExtractGSRFeatures(
            cvx_hdf5_key='/iguazu/signal/gsr/cvx',
            scrpeaks_hdf5_key='/iguazu/signal/gsr/scrpeaks',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/features/gsr/sequence',
        )
        notify = SlackTask(message='Cardiac feature extraction finished!')

        with self:
            # Signal processing branch
            clean_signals = clean.map(signals=raw_signals, annotations=raw_signals, events=events)
            downsample_signals = downsample.map(signals=clean_signals, annotations=clean_signals)
            cvx_signals = cvx.map(signals=downsample_signals, annotations=downsample_signals)
            scr_peaks = scrpeaks.map(signals=cvx_signals, annotations=cvx_signals)

            # Feature extraction
            features = extract_features.map(cvx=cvx_signals,
                                            scrpeaks=scr_peaks,
                                            events=events,
                                            parent=raw_signals)

            # Send slack notification
            notify(upstream_tasks=[features])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()


class GalvanicSummaryFlow(PreparedFlow):
    """Collect all  cardiac features in a single CSV file"""

    REGISTRY_NAME = 'summarize_galvanic'
    DEFAULT_QUERY = f"""
SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
       base->>'filename' AS filename,  -- this is just to help the human debugging this
       omi->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
       iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
FROM   metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%gsr_features.hdf5'         -- Only HDF5 files TODO: remove _gsr_features hack
AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
ORDER BY id                                -- always in the same order
"""

    def _build(self,
               **kwargs):

        # Manage parameters
        kwargs = kwargs.copy()
        # Propagate workspace name because we captured it on kwargs
        kwargs['workspace_name'] = workspace_name
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omi=None,
            standard=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families

        # When the query is set by kwargs, leave the query and dialect as they
        # come. Otherwise, set to the default defined just above
        if not kwargs.get('query', None):
            kwargs['query'] = self.DEFAULT_QUERY
            kwargs['dialect'] = 'postgresql_json'

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        features_files = dataset_flow.terminal_tasks().pop()

        # instantiate tasks. Use separate tasks for a classic ETL approach:
        # E: read features from HDF5 file
        # T and L: merge features into a single dataframe, then save as CSV
        read_features = LoadDataframe(
            key='/iguazu/features/gsr/sequence',
        )
        merge_features = MergeDataframes(
            filename='galvanic_summary.csv',
            path='datasets',
        )
        notify = SlackTask(message='Galvanic feature summarization finished!')

        with self:
            feature_dataframes = read_features.map(file=features_files)
            merged_dataframe = merge_features(parents=features_files, dataframes=feature_dataframes)
            # Send slack notification
            notify(upstream_tasks=[merged_dataframe])

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
