import datetime
import logging

from prefect import Flow
from prefect.tasks.notifications import SlackTask


from iguazu.cache_validators import ParametrizedValidator
from iguazu.flows.datasets import generic_dataset_flow
from iguazu.tasks.common import MergeFilesFromGroups
from iguazu.tasks.galvanic import CleanSignal, ApplyCVX, DetectSCRPeaks, RemoveBaseline
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.summarize import ExtractFeatures
from iguazu.tasks.unity import ExtractSequences
from iguazu.recipes import inherit_params, register_flow


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
        galvanic=None,
        omi=None,
        vr_sequences=None,
        task=None,
    )
    families = kwargs.get('families', {}) or {}  # Could be None by default args
    for name in required_families:
        families.setdefault(name, required_families[name])
    kwargs['families'] = families
    # In case there was no query, set a default one
    default_query = """\
        SELECT
        id,
        filename
        FROM base
        LEFT JOIN iguazu USING (id)
        LEFT JOIN omi using (id)
        WHERE
            base.filename LIKE '%.hdf5' AND      -- only HDF5 files
            iguazu.id IS NULL AND                -- files *not* created by iguazu
            iguazu.gsr::json->>'status' IS NULL  -- files not yet processed by iguazu
        LIMIT 10
    """
    default_alt_query = """\
        SELECT
        id,
        filename
        FROM base
        LEFT JOIN iguazu USING (id)
        WHERE
            base.filename LIKE '%.hdf5' AND      -- only HDF5 files
            iguazu.id IS NULL                    -- files *not* created by iguazu
        LIMIT 10
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
        sampling_rate=256,
        force=force,
        # Prefect task arguments
        state_handlers=[logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    apply_cvx = ApplyCVX(
        # Iguazu task constructor arguments
        signal_column='F_filtered_clean_inversed_zscored',
        warmup_duration=15,
        threshold_scr=4,
        force=force,
        # Prefect task arguments
        state_handlers=[logging_handler],
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
        state_handlers=[logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    report_sequences = ExtractSequences(
        # Iguazu task constructor arguments
        sequences=None,
        force=force,
        # Prefect task arguments
        state_handlers=[logging_handler],
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
        state_handlers=[logging_handler],
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
        state_handlers=[logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    baseline_sequences = ['lobby_sequence_0', 'lobby_sequence_1', 'physio-sonification_survey_0',
                          'cardiac-coherence_survey_0', 'cardiac-coherence_survey_1',
                          'cardiac-coherence_score_0']
    correct_scr = RemoveBaseline(
        # Iguazu task constructor arguments
        features_group="/gsr/features/scr",
        output_group="/gsr/features/scr_corrected",
        sequences=baseline_sequences,
        columns=['gsr_SCR_peaks_detected_rate'],
        name='RemoveBaseline__scr',
        force=force,
        # Prefect task arguments
        state_handlers=[logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    correct_scl = RemoveBaseline(
        # Iguazu task constructor arguments
        features_group="/gsr/features/scl",
        output_group="/gsr/features/scl_corrected",
        sequences=baseline_sequences,
        columns=[
            'gsr_SCL_median',
            'gsr_SCL_ptp',
            'gsr_SCL_linregress_slope',
            'gsr_SCL_auc'
        ],
        name='RemoveBaseline__scl',
        force=force,
        # Prefect task arguments
        state_handlers=[logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(force=force),
    )
    merge_subject = MergeFilesFromGroups(
        # Iguazu task constructor arguments
        suffix="_gsr",
        status_metadata_key='gsr',
        # Prefect task arguments
        state_handlers=[logging_handler],
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
        cvx = apply_cvx.map(clean_signals)
        scr = detect_scr_peaks.map(cvx)

        # Event handling branch
        sequences_reports = report_sequences.map(events=events)

        # Feature extraction (merge of signal pre-processing and event handling)
        scr_features = extract_features_scr.map(signals=scr, report=sequences_reports)
        scl_features = extract_features_scl.map(signals=cvx, report=sequences_reports)

        # Baseline feature correction
        scr_features_corrected = correct_scr.map(features=scr_features)
        scl_features_corrected = correct_scl.map(features=scl_features)

        # Subject summary
        merged = merge_subject.map(parent=raw_signals,
                                   gsr_timeseries_deconvoluted=cvx,
                                   gsr_features_scr=scr_features_corrected,
                                   gsr_features_scl=scl_features_corrected,
                                   unity_sequences=sequences_reports)

        # Send slack notification
        notify(upstream_tasks=[merged])

        # TODO: what's the reference task of this flow?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow

