import logging

import click
from prefect import Parameter

from iguazu import __version__
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.cardiac import CleanPPGSignal, ExtractHRVFeatures, SSFPeakDetect
from iguazu.tasks.common import SlackTask
from iguazu.tasks.signals import ExtractPeaks
from iguazu.tasks.summarize import SummarizePopulation

logger = logging.getLogger(__name__)


class CardiacFeaturesFlow(PreparedFlow):
    """Extract all  cardiac features from a file dataset"""

    REGISTRY_NAME = 'features_cardiac'
    DEFAULT_QUERY = f"""
SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
       base->>'filename' AS filename,  -- this is just to help the human debugging this
       omi->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
       iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
FROM   metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
AND    (standard->'standardized')::bool        -- Only standardized files
AND    standard->'groups' ? '/iguazu/signal/ppg/standard' -- containing the PPG signal
AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
AND    iguazu->>'version' <= '{__version__}'    -- by this iguazu version or earlier
ORDER BY id                                    -- always in the same order
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
        clean = CleanPPGSignal(
            signals_hdf5_key='/iguazu/signal/ppg/standard',
            output_hdf5_key='/iguazu/signal/ppg/clean',
        )
        detect_peaks = SSFPeakDetect(
            signals_hdf5_key='/iguazu/signal/ppg/clean',
            ssf_output_hdf5_key='/iguazu/signal/ppg/ssf',
            nn_output_hdf5_key='/iguazu/signal/ppg/NN',
            nni_output_hdf5_key='/iguazu/signal/ppg/NNi',
        )
        extract_features = ExtractHRVFeatures(
            nn_hdf5_key='/iguazu/signal/ppg/NN',
            nni_hdf5_key='/iguazu/signal/ppg/NNi',
        )

        # plot_signals = PPGReport()
        # noop = Task(name='noop')
        notify = SlackTask(message='Cardiac feature extraction finished!')

        with self:
            # plot_param = Parameter('plot', default=plot, required=False)
            # Signal processing branch
            clean_signals = clean.map(signals=raw_signals)
            preprocessed_signals = detect_peaks.map(signals=clean_signals)
            # Feature extraction
            features = extract_features.map(nn=preprocessed_signals,
                                            nni=preprocessed_signals,
                                            events=events,
                                            parent=raw_signals)

            # Send slack notification
            notify(upstream_tasks=[features])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options() #+ (
    #         click.option('--plot/--no-plot', is_flag=True, default=True, show_default=True,
    #                      help='Add plotting tasks to the flow.'),
    #     )


# class PPGPeakExtraction(PreparedFlow):
#     """Preprocess PPG signals and extract all possible peaks"""
#
#     REGISTRY_NAME = 'extract_ppg_peaks'
#
#     def _build(self, **kwargs):
#         # Force required families: Quetzal workspace must have the following
#         # families: (nb: None means "latest" version)
#         required_families = dict(
#             iguazu=None,
#             omi=None,
#             standard=None,
#         )
#         families = kwargs.get('families', {}) or {}  # Could be None by default args
#         for name in required_families:
#             families.setdefault(name, required_families[name])
#         kwargs['families'] = families
#
#         # Default query, in human terms: "All HDF5 files with standardized signals"
#         default_query = """\
#             SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
#                    base->>'filename' AS filename,  -- this is just to help the human debugging this
#                    omi->>'user_hash' AS user_hash  -- this is just to help the openmind human debugging this
#             FROM   metadata
#             WHERE  base->>'state' = 'READY'                -- No temporary files
#             AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
#             AND    iguazu->>'status' = 'SUCCESS'           -- Only files generated without errors
#             AND    standard->>'standardized' = 'true'      -- Only standardized files...
#             AND    standard->'groups' @> '["/iguazu/signal/ppg/standard"]'::jsonb -- ...that contain the PPG signal
#             ORDER BY id                                    -- always in the same order
#         """
#
#         # When the query is set by kwargs, leave the query and dialect as they
#         # come. Otherwise, set to the default defined just above
#         if not kwargs.get('query', None):
#             kwargs['query'] = default_query
#             kwargs['dialect'] = 'postgresql_json'
#
#         # This flow requires an upstream dataset flow in order to provide the
#         # input files. Create one and deduce the tasks to plug the cardiac flow
#         # to the output of the dataset flow
#         dataset_flow = GenericDatasetFlow(**kwargs)
#         raw_signals = dataset_flow.terminal_tasks().pop()
#         self.update(dataset_flow)
#
#         # Instantiate tasks
#         clean = CleanPPGSignal(
#             signals_hdf5_key='/iguazu/signal/ppg/standard',
#             output_hdf5_key='/iguazu/signal/ppg/clean',
#         )
#         extract_peaks = ExtractPeaks(
#             signals_hdf5_key='/iguazu/signal/ppg/clean',
#             output_hdf5_key='/iguazu/peaks/ppg',
#             column='SSF_PPG',
#         )
#
#         with self:
#             clean_signals = clean.map(signals=raw_signals)
#             peaks = extract_peaks.map(signal=clean_signals)
#
#         logger.debug('Built flow %s with tasks %s', self, self.tasks)
#
#     @staticmethod
#     def click_options():
#         return GenericDatasetFlow.click_options()


class CardiacSummaryFlow(PreparedFlow):
    """Collect all  cardiac features in a single CSV file"""

    REGISTRY_NAME = 'summarize_cardiac'

    def _build(self, *,
               workspace_name=None, query=None, alt_query=None,
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
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families
        # This is the main query that defines the dataset for merging the galvanic
        # features. There is a secondary query because some of the tables may not
        # be available on a new workspace.
        default_query = """\
            SELECT
                id,
                filename
            FROM base
            LEFT JOIN iguazu USING (id)
            LEFT JOIN omi using (id)
            WHERE
                base.state = 'READY' AND                    -- no temporary files
                base.filename LIKE '%_ppg.hdf5' AND         -- only HDF5 files
                COALESCE(iguazu."MergeFilesFromGroups", '{{}}')::json->>'state' = 'SUCCESS' AND -- Only files whose mergefilefromgroups was successful
                COALESCE(iguazu."MergeFilesFromGroups", '{{}}')::json->>'version' = '{version}'     -- On this particular iguazu version
            ORDER BY base.id                                -- always in the same order
        """.format(version=__version__)  # Note the {{}} to avoid formatting the coalesce terms
        # There is no secondary query because this flow only makes sense *after*
        # the galvanic extract features flow has run
        default_alt_query = None
        kwargs['query'] = query or default_query
        kwargs['alt_query'] = alt_query or default_alt_query

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        features_files = dataset_flow.terminal_tasks().pop()

        # instantiate tasks
        merge_population = SummarizePopulation(
            # Iguazu task constructor arguments
            groups={'hrv_features': None},  # TODO: I dont understand why use _ instead of / since we are talking about groups
            filename='cardiac_summary',
            # # Prefect task arguments
            # state_handlers=[garbage_collect_handler, logging_handler],
            # cache_for=datetime.timedelta(days=7),
            # cache_validator=ParametrizedValidator(),
        )
        notify = SlackTask(message='Cardiac feature summarization finished!')

        with self:
            population_summary = merge_population(features_files)

            # Send slack notification
            notify(upstream_tasks=[population_summary])

            # TODO: what's the reference task of this flow?

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
