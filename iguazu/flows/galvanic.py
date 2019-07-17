import os
import tempfile
import time
import traceback

import click
import pandas as pd
from prefect import Flow, Parameter, context
from prefect.engine.executors import LocalExecutor, SynchronousExecutor
from prefect.engine.state import Mapped, Failed
from prefect.tasks.control_flow import switch, merge

from iguazu.cache_validators import all_validator
from iguazu.executors import DaskExecutor
from iguazu.flows.datasets import generic_dataset_flow
from iguazu.tasks.common import ListFiles, MergeFilesFromGroups
from iguazu.tasks.galvanic import CleanSignal, ApplyCVX, DetectSCRPeaks, RemoveBaseline
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace, Query
from iguazu.tasks.summarize import ExtractFeatures
from iguazu.tasks.unity import ReportSequences
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
        warmup_duration=30,
        glitch_kwargs=dict(
            scaling='robust',
            nu=1,
            range=(-0.02, +0.02),
            rejection_win=35,
        ),
        interpolation_kwargs=dict(
            method='pchip',
        ),
        lowpass_kwargs=dict(
            Wn=[35],
            order=5,
        ),
        scaling_kwargs=dict(
            method='standard',
        ),
        corrupted_maxratio=0.3,
        #force=force,
        state_handlers=[logging_handler],
        #cache_for=datetime.timedelta(days=7),
        #cache_validator=all_validator(force=force),
    )
    apply_cvx = ApplyCVX(
        warmup_duration=15,
        glitch_kwargs=dict(
            scaling=False,
            nu=0,
            range=(0, 4),
            rejection_win=20,
        ),
        cvxeda_kwargs=None,
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    detect_scr_peaks = DetectSCRPeaks(
        warmup_duration=15,
        glitch_kwargs=dict(
            nu=0,
            range=(0, 7),
        ),
        peak_detection_kwargs=dict(
            width=0.5,
            prominence=0.1,
            prominence_window=15,
        ),
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    report_sequences = ReportSequences(
        sequences=None,
        # force=force,
        state_handlers=[logging_handler],
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    extract_features_scr = ExtractFeatures(
        signals_group="/gsr/timeseries/scrpeaks",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/scr",
        feature_definitions=dict(
            rate={
                "class": "numpy.sum",
                "columns": ["SCR_peaks_detected"],
                "divide_by_duration": True,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            },
            median={
                "class": "numpy.nanmedian",
                "columns": ['SCR_peaks_increase-duration', 'SCR_peaks_increase-amplitude'],
                "divide_by_duration": False,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            }
        ),
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    scl_columns_definitions_kwargs = dict(
        columns=['F_clean_inversed_lowpassed_zscored_SCL'],
        divide_by_duration=False,
        empty_policy='bad',
        drop_bad_sample=True,
    )
    extract_features_scl = ExtractFeatures(
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
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    baseline_sequences = ['lobby_sequence_0', 'lobby_sequence_1', 'physio-sonification_survey_0',
                          'cardiac-coherence_survey_0', 'cardiac-coherence_survey_1',
                          'cardiac-coherence_score_0']
    correct_scr = RemoveBaseline(
        features_group="/gsr/features/scr",
        output_group="/gsr/features/scr_corrected",
        sequences=baseline_sequences,
        columns=['SCR_peaks_detected_rate'],
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
    )
    correct_scl = RemoveBaseline(
        features_group="/gsr/features/scl",
        output_group="/gsr/features/scl_corrected",
        sequences=baseline_sequences,
        columns=[
            'F_clean_inversed_lowpassed_zscored_SCL_median',
            'F_clean_inversed_lowpassed_zscored_SCL_ptp',
            'F_clean_inversed_lowpassed_zscored_SCL_linregress_slope',
            'F_clean_inversed_lowpassed_zscored_SCL_auc'
        ],
        # force=force,
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )
    merge_subject = MergeFilesFromGroups(
        suffix="_gsr",
        state_handlers=[logging_handler],
        # skip_on_upstream_skip=False,
        # cache_for=datetime.timedelta(days=7),
        # cache_validator=all_validator(force=force),
    )

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
        merge_subject.map(parent=raw_signals,
                          gsr_timeseries_deconvoluted=cvx,
                          gsr_features_scr=scr_features_corrected,
                          gsr_features_scl=scl_features_corrected,
                          unity_sequences=sequences_reports)

        # TODO: what's the reference task of this?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow

