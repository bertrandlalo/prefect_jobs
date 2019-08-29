import datetime
import itertools
import logging

from prefect import Flow

from iguazu import __version__
from iguazu.cache_validators import ParametrizedValidator
from iguazu.flows.datasets import generic_dataset_flow
from iguazu.recipes import inherit_params, register_flow
from iguazu.tasks.common import MergeFilesFromGroups, SlackTask
from iguazu.tasks.galvanic import ApplyCVX, CleanSignal, DetectSCRPeaks, Downsample
from iguazu.tasks.handlers import garbage_collect_handler, logging_handler
from iguazu.tasks.spectral import BandPowers
from iguazu.tasks.summarize import ExtractFeatures
from iguazu.tasks.unity import ExtractSequences


logger = logging.getLogger(__name__)


@register_flow('galvanic_features')
@inherit_params(generic_dataset_flow)
def galvanic_features_flow(*, force=False, workspace_name=None, query=None, alt_query=None,
                           **kwargs) -> Flow:
    """Extract galvanic features"""
    logger.debug('Creating galvanic features flow')

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
    # This is the main query that defines the dataset for extracting galvanic
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
            base.state = 'READY' AND                 -- no temporary files
            base.filename LIKE '%.hdf5' AND          -- only HDF5 files
            (
                iguazu.gsr::json->>'status' IS NULL OR  -- files not fully processed by iguazu on this flow
                COALESCE(iguazu.gsr::json->>'version', '0') < '{version}' -- or files not processed by this version of iguazu
            ) AND
            iguazu.parents is NULL                   -- files not generated by iguazu
        ORDER BY base.id                             -- always in the same order
    """.format(version=__version__)
    # This secondary, alternative query is defined for the case when a new
    # quetzal workspace is created, and the iguazu.gsr metadata does not even
    # exist. We need to to do this because the iguazu.gsr column does not exist
    # and postgres does not permit querying a non-existent column
    default_alt_query = """\
        SELECT
            id,
            filename
        FROM base
        LEFT JOIN iguazu USING (id)
        WHERE
            base.state = 'READY' AND             -- no temporary files
            base.filename LIKE '%.hdf5'          -- only HDF5 files
        ORDER BY base.id                         -- always in the same order
    """
    kwargs['query'] = query or default_query
    kwargs['alt_query'] = alt_query or default_alt_query

    # Manage connections to other flows
    dataset_flow = generic_dataset_flow(**kwargs)
    raw_signals = dataset_flow.terminal_tasks().pop()
    events = raw_signals

    # Instantiate tasks
    clean = CleanSignal(
        # Iguazu task constructor arguments
        signal_column='F',
        warmup_duration=30,
        quality_kwargs=dict(
            sampling_rate=512,
            oa_range=(1e-6, 2000),
            glitch_range=(0.0, 180),
            rejection_window=2,
        ),
        interpolation_kwargs=dict(
            method='pchip',
        ),
        filter_kwargs=dict(
            order=10,
            frequencies=30,
            filter_type='lowpass',
        ),
        scaling_kwargs=dict(
            method='standard',
        ),
        corrupted_maxratio=0.3,
        sampling_rate=512,
        force=force,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    downsample = Downsample(
        # Iguazu task constructor arguments
        sampling_rate=256,
        force=force,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    apply_cvx = ApplyCVX(
        # Iguazu task constructor arguments
        signal_column='F_filtered_clean_inversed_zscored',
        warmup_duration=15,
        threshold_scr=4,
        epoch_size=300,
        epoch_overlap=60,
        force=force,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    detect_scr_peaks = DetectSCRPeaks(
        # Iguazu task constructor arguments
        signal_column='gsr_SCR',
        warmup_duration=15,
        peaks_kwargs=dict(
            width=0.5,
            prominence=.1,
            prominence_window=15,
            rel_height=.5,
        ),
        max_increase_duration=7,  # seconds
        force=force,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    report_sequences = ExtractSequences(
        # Iguazu task constructor arguments
        sequences=None,
        force=force,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    bands = dict(
        # Classic HRV bands      # Number of bins for 60 seconds @ 512 Hz
        # ULF=(0.0001, 0.0033),    # 0 bins (empty!!!)
        VLF=(0.003, 0.04),       # 2 bins
        LF=(0.04, 0.15),         # 6 bins
        HF=(0.15, 0.40),         # 15 bins
        VHF=(0.4, 0.5),          # 6 bins
        # 5Hz wide division of the rest of the signal
        VHF1=(1.0, 5.0),         # 240 bins
        VHF2=(5.0, 10.0),        # 300 bins
        VHF3=(10.0, 15.0),       # 300 bins
        VHF4=(15.0, 20.0),       # 300 bins
        VHF5=(20.0, 25.0),       # 300 bins
        VHF6=(25.0, 30.0),       # 300 bins
    )
    band_powers = BandPowers(
        # Iguazu task constructor arguments
        signal_group='/gsr/timeseries/preprocessed',
        signal_column='F_filtered_clean_inversed',
        epoch_size=60,     # 60 second epochs
        epoch_overlap=59,  # one epoch every second
        bands=bands,
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    band_powers_features = ExtractFeatures(
        # Iguazu task constructor arguments
        signals_group="/gsr/timeseries/bandpowers",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/spectral",
        feature_definitions=dict(
            median={
                "class": "numpy.nanmedian",  # TODO: a geometric mean may be better
                "columns": ['_'.join(tup) for tup in itertools.product(['F_filtered_clean_inversed'], bands.keys())],   # TODO: some way to say all columns
                "divide_by_duration": False,
                "empty_policy": 'bad',
                "drop_bad_samples": True,
            },
        ),
        force=force,
        # Prefect task arguments
        name='ExtractFeatures_bp',
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    extract_features_scr = ExtractFeatures(
        # Iguazu task constructor arguments
        signals_group="/gsr/timeseries/scrpeaks",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/scr",
        feature_definitions=dict(
            rate={
                "class": "numpy.sum",
                "columns": ["gsr_SCR_peaks_detected"],
                "divide_by_duration": True,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            },
            median={
                "class": "numpy.nanmedian",
                "columns": ['gsr_SCR_peaks_increase-duration', 'gsr_SCR_peaks_increase-amplitude'],
                "divide_by_duration": False,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            }
        ),
        force=force,
        # Prefect task arguments
        name='ExtractFeatures__scr',
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    scl_columns_definitions_kwargs = dict(
        columns=['gsr_SCL'],
        divide_by_duration=False,
        empty_policy='bad',
        drop_bad_sample=True,
    )
    extract_features_scl = ExtractFeatures(
        # Iguazu task constructor arguments
        signals_group="/gsr/timeseries/deconvoluted",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/scl",
        feature_definitions={
            "median": {
                "class": "numpy.nanmedian",
                **scl_columns_definitions_kwargs,
            },
            "std": {
                "class": "numpy.nanstd",
                **scl_columns_definitions_kwargs,
            },
            "ptp": {
                "class": "numpy.ptp",
                **scl_columns_definitions_kwargs,
            },
            "linregress": {
                "custom": "linregress",  # TODO: why is this custom and the other ones are class?
                **scl_columns_definitions_kwargs,
            },
            "auc": {
                "custom": "auc",
                **scl_columns_definitions_kwargs,
            },
        },
        force=force,
        # Prefect task arguments
        name='ExtractFeatures__scl',
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    merge_subject = MergeFilesFromGroups(
        # Iguazu task constructor arguments
        suffix="_gsr",
        status_metadata_key='gsr',
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    notify = SlackTask(message='Galvanic feature extraction finished!')

    # Define flow and its task connections
    with Flow('galvanic_features_flow') as flow:
        # Connect/extend this flow with the dataset flow
        flow.update(dataset_flow)

        # Galvanic features flow:
        # Signal pre-processing branch: Clean -> CVX -> SCR
        clean_signals = clean.map(signal=raw_signals, events=events)
        clean_signals_256 = downsample.map(signal=clean_signals)
        cvx = apply_cvx.map(clean_signals_256)
        scr = detect_scr_peaks.map(cvx)

        # band power branch
        powers = band_powers.map(signal=clean_signals)

        # Event handling branch
        sequences_reports = report_sequences.map(events=events)

        # Feature extraction (merge of signal pre-processing and event handling)
        scr_features = extract_features_scr.map(signals=scr, report=sequences_reports)
        scl_features = extract_features_scl.map(signals=cvx, report=sequences_reports)
        bp_features = band_powers_features.map(signals=powers, report=sequences_reports)

        # Subject summary
        merged = merge_subject.map(parent=raw_signals,
                                   gsr_timeseries_deconvoluted=cvx,
                                   gsr_features_scr=scr_features,
                                   gsr_features_scl=scl_features,
                                   bp_features=bp_features,
                                   unity_sequences=sequences_reports)

        # Send slack notification
        notify(upstream_tasks=[merged])

        # TODO: what's the reference task of this flow?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow

