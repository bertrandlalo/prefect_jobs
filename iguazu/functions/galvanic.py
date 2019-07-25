import logging

import numpy as np
import pandas as pd
from dsu.cvxEDA import apply_cvxEDA
from dsu.dsp.filters import inverse_signal, filtfilt_signal, scale_signal, drop_rows
from dsu.dsp.peaks import detect_peaks
from dsu.quality import quality_gsr
from sklearn.preprocessing import RobustScaler

from iguazu.helpers.tasks import IguazuError  # Todo: move IguazuError to a module exceptions.py


logger = logging.getLogger(__name__)


def galvanic_clean(data, events, column, warmup_duration, quality_kwargs, interpolation_kwargs, filter_kwargs,
                   scaling_kwargs, corrupted_maxratio, sampling_rate):
    """
     Preprocess the galvanic data and detect bad quality samples.
     It should be noted that some steps here are specific to the device we use, ie. Nexus from MindMedia.
     Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
     devices might have different behaviors.

    The pipeline will:

        - detect bad samples calling :py:func:dsu.quality.detect_bad_from_amplitude with `glitch_kwargs`
        - lowpass the resulting signal using :py:func:dsu.filters.dsp.bandpass_signal with `filter_kwargs`
        - decimate signal at rate `sampling_rate`
        - remove the bad samples and evaluate the corruption ratio. If too high, then raise an error.
        - interpolate the missing signal e calling :py:meth:pandas.Series.interpolat with `interpolation_kwargs`.
        - inverse the signal to access galvanic conductance (G=1/R)
        - scale the signal on the whole session using using :py:func:dsu.filters.dsp.scale_signal with `scaling_kwargs`

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the raw GSR in channel given by column_name.
    events: pd.DataFrame
        Dataframe with 2 columns: [label, data], containing string labels and serialized meta giving the context of the labels.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration (in s) to select before and after the vr session (to avoid side effects in the future
    processing steps, ie. that we can then set to bad ).
    quality_kwargs:
        Keywords arguments to detect bad samples.
    interpolation_kwargs:
        Keywords arguments to interpolate the missing (bad) samples.
    filter_kwargs:
        Keywords arguments to lowpass the data.
    scaling_kwargs:
        Keywords arguments to scale the data.
    corrupted_maxratio: float
        Maximum acceptable ratio of corrupted (bad) samples.
    sampling_rate: float
        Rate of output signal (after decimation)

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns 'F', 'F_clean', 'F_clean_inversed', 'F_clean_inversed_lowpassed', 'F_clean_inversed_lowpassed_zscored', 'bad'

    Examples
    --------

        .. image:: ../source/_static/examples/galvanic_functions/io_clean.png

    """
    if not events.index.is_monotonic:
        raise Exception('Events index should be monotonic. ')

    warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
    begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session

    # troncate dataframe on session times
    data = data[begins:ends]
    data = data.loc[:, [column]]

    # lowpass filter signal
    data = filtfilt_signal(data, columns=[column],
                           **filter_kwargs, suffix='_filtered')

    # add a column "bad" with rejection boolean on Amplifier and HF (glitches) criteria
    data = quality_gsr(data, column=column + '_filtered', **quality_kwargs)
    # estimate the corrupted ratio
    # if too many samples were dropped, raise an error
    corrupted_ratio = data.bad.mean()
    if corrupted_ratio > corrupted_maxratio:
        raise IguazuError('Artifact corruption of %s exceeds  %s.', corrupted_ratio, corrupted_maxratio)
    # make a copy of the signal with suffix "_clean", mask bad samples
    data_clean = data[[column + '_filtered']].copy().add_suffix('_clean').mask(data.bad)
    # Pandas does not like tz-aware timestamps when interpolating
    if data_clean.index.tzinfo is None:
        # old way: tz-naive
        data_clean.interpolate(**interpolation_kwargs, inplace=True)
    else:
        # new way: with timezone. Convert to tz-naive, interpolate, then back to tz-aware
        data_clean = (
            data_clean.set_index(data_clean.index.tz_convert(None))
                .interpolate(**interpolation_kwargs)
                .set_index(data_clean.index)
        )

    # Pandas does not like tz-aware timestamps when interpolating
    if data_clean.index.tzinfo is None:
        # old way: tz-naive
        data_clean.interpolate(**interpolation_kwargs, inplace=True)
    else:
        # new way: with timezone. Convert to tz-naive, interpolate, then back to tz-aware
        data_clean = (
            data_clean.set_index(data_clean.index.tz_convert(None))
                .interpolate(**interpolation_kwargs)
                .set_index(data_clean.index)
        )
    # take inverse to have the SKIN CONDUCTANCE G = 1/R = I/U
    data_clean = inverse_signal(data_clean, columns=[column + '_filtered_clean'], suffix='_inversed')

    # scale signal on the all session
    data_clean = scale_signal(data_clean, columns=[column + '_filtered_clean_inversed'], suffix='_zscored',
                              **scaling_kwargs)

    # return preprocessed data
    data = pd.concat([data, data_clean], axis=1)

    # decimate signal
    data = drop_rows(data, sampling_rate)

    return data


def galvanic_cvx(data, column=None, warmup_duration=15, threshold_scr=4., cvxeda_params=None):
    """ Separate phasic (SCR) and tonic (SCL) galvanic components using a convexe deconvolution.

    Parameters
    ----------
    data: pd.ataFrame
        Dataframe containing the preprocessed GSR in channel given by column_name.
    column: str | None
        Name of column where the data of interest are located.
        If None, the first column is considered.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    threshold_scr:
        Maximum acceptable amplitude of SCR component.
    cvxeda_params:
        Keywords arguments to apply cvxEDA algorithm.

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns: ['F_clean_inversed_lowpassed_zscored_SCR', 'F_clean_inversed_lowpassed_zscored°SCL', 'bad']

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_deconvolution.png

    """
    cvxeda_params = cvxeda_params or {}
    # extract SCR and SCL component using deconvolution toolbox cvxEDA

    if 'bad' not in data:
        raise Exception('Received data without a column named "bad"')

    bad = data.bad

    # if no column is specified, consider the first one
    column = column or data.columns[0]

    # Deconvolution or the signal
    data = apply_cvxEDA(data[[column, 'bad']].dropna(), column=column, **cvxeda_params)

    # add a column "bad" with rejection boolean on amplitude criteria
    data.loc[:, 'bad'] = bad
    data.loc[data[column + '_SCR'] >= threshold_scr, 'bad'] = True

    # set warmup period to "bad"
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    # TODO: this does not do what it's supposed to do; it should be a slice!
    data.loc[:data.index[0] + warm_up_timedelta, 'bad'] = True
    data.loc[data.index[-1] - warm_up_timedelta:, 'bad'] = True

    # replace column string name by 'gsr' for lisibility purpose
    data.columns = data.columns.str.replace(column, 'gsr')

    return data


def galvanic_scrpeaks(data, column=None, warmup_duration=15, peaks_kwargs=None, max_increase_duration=7):
    """ Detect peaks of SCR component and estimate their characteristics.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the deconvoluted GSR in channel given by column_name.
    column: str | None
        Name of column where the data of interest are located.
        If None, the first column is considered.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    peaks_kwargs:
        Keywords arguments to detect peaks and define their characteristics.
    max_increase_duration:
        Maximum duration for the peak to rise

    Returns
    -------
     data : pd.DataFrame
            Dataframe with columns: ['SCR', 'SCR_peaks_detected', 'SCR_peaks_increase-duration',
                                'SCR_peaks_increase-amplitude',
                                'SCR_peaks_recovery-duration', 'bad']

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_scrpeaks.png


    """
    # convert duration (s) in timedelta
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')

    if 'bad' not in data:
        raise ValueError('Received data without a column named "bad"')

    bad = data.bad

    # if no column is specified, consider the first one
    column = column or data.columns[0]

    # Select the data of interest
    data = data.loc[:, [column]]
    data = data[data.index[0] + warm_up_timedelta:data.index[-1] - warm_up_timedelta]

    # Define the scaler to apply before detecting peaks
    scaler = RobustScaler(with_centering=True, quantile_range=(5, 95.0))

    # Detect peaks and estimate their properties
    data = detect_peaks(data, column=column, estimate_properties=True, scaler=scaler, **peaks_kwargs)
    data = data[data.label == 'peak'].loc[:,
           ['value', 'left_local', 'left_prominence', 'right_ips']]

    # Rename columns for lisibility purposes
    data = data.rename(
        columns={
            'value': column + '_peaks_value',
            'left_local': column + '_peaks_increase-duration',
            'left_prominence': column + '_peaks_increase-amplitude',
            'right_ips': column + '_peaks_recovery-duration'
        })

    # Append the 'bad' column from input data
    data.loc[:, 'bad'] = bad
    # Update the bad column with this new find of artefact, being false peak detection
    # (when thee increase duration is greater than the prominence window,
    # it means no local minima has been found, hence the peak was not significant)
    data.loc[data[column + '_peaks_increase-duration'] >= max_increase_duration, 'bad'] = True
    # To ease the extraction of peak rate, let's add a column with boolean values
    # True if the peak is kept, False if not.
    data.loc[:, column + '_peaks_detected'] = ~data.bad

    return data


def galvanic_baseline_correction(features, sequences, columns=None):
    """ Estimate basal state for features on pseudo-baseline sequences and remove it.

    Parameters
    ----------
    features: pd.DataFrame
        Dataframe with features where index are periods and columns are feature names.
    sequences: list
        List of period names to compute the pseudo baseline.
    columns: list
        List of columns where the baseline correction should be applied.

    Returns
    -------
    features_corrected: pd.DataFrame
        Dataframe with the same shape as the input `features`, after removal of the
        basal state.
    valid_sequences_ratio: Dict
        Dictionary where keys are the feature names and values are the ratio of
        valid periods where it (the feature) could be estimated.

    Examples
    --------

    >>> features
    name                                               F_clean_inversed_lowpassed_zscored_SCL_median  ... F_clean_inversed_lowpassed_zscored_SCL_auc
    physio-sonification_sequence_0                                                               bad  ...                                   -168.801
    lobby_sequence_0                                                                             bad  ...                                   -7.03184
    lobby_sequence_1                                                                             bad  ...                                   -18.9236
    lobby_sequence_2                                                                             bad  ...                                    22.3149
    space-stress_game_0                                                                          bad  ...                                    208.325
    space-stress_game_1                                                                          bad  ...                                    157.129
    common_respiration-calibration_data-accumulation_0                                           bad  ...                                        bad
    space-stress_game_enemy-wave_0                                                               bad  ...                                   -2.06235
    space-stress_game_enemy-wave_1                                                               bad  ...                                    19.7417
    space-stress_game_enemy-wave_2                                                               bad  ...                                    50.4054
    ...
    space-stress_intro_0                                                                         bad  ...                                   -20.1367
    physio-sonification_coherence-feedback_0                                                     bad  ...                                   -24.4899
    cardiac-coherence_score_0                                                                    bad  ...                                   -27.0506
    cardiac-coherence_survey_0                                                                   bad  ...                                   -8.21526
    cardiac-coherence_survey_1                                                                   bad  ...                                   -72.0361
    cardiac-coherence_data-accumulation_0                                                        bad  ...                                   -177.136
    intro_calibration_0                                                                          bad  ...                                    10.6846
    >>> sequences
        ['lobby_sequence_0', 'lobby_sequence_1', 'physio-sonification_survey_0', 'cardiac-coherence_survey_0', 'cardiac-coherence_survey_1', 'cardiac-coherence_score_0']
    >>> features_corrected, valid_sequences_ratio = galvanic_baseline_correction(features, sequences, columns=None)
    >>> features_corrected
    name                                               F_clean_inversed_lowpassed_zscored_SCL_median  ... F_clean_inversed_lowpassed_zscored_SCL_auc
    physio-sonification_sequence_0                                                               bad  ...                                   -142.678
    lobby_sequence_0                                                                             bad  ...                                    19.0911
    lobby_sequence_1                                                                             bad  ...                                    7.19937
    lobby_sequence_2                                                                             bad  ...                                    48.4378
    space-stress_game_0                                                                          bad  ...                                    234.448
    space-stress_game_1                                                                          bad  ...                                    183.252
    common_respiration-calibration_data-accumulation_0                                           bad  ...                                        bad
    space-stress_game_enemy-wave_0                                                               bad  ...                                    24.0606
    space-stress_game_enemy-wave_1                                                               bad  ...                                    45.8647
    space-stress_game_enemy-wave_2                                                               bad  ...                                    76.5284
    ...
    space-stress_intro_0                                                                         bad  ...                                    5.98628
    physio-sonification_coherence-feedback_0                                                     bad  ...                                    1.63304
    cardiac-coherence_score_0                                                                    bad  ...                                   -0.92763
    cardiac-coherence_survey_0                                                                   bad  ...                                    17.9077
    cardiac-coherence_survey_1                                                                   bad  ...                                   -45.9132
    cardiac-coherence_data-accumulation_0                                                        bad  ...                                   -151.013
    intro_calibration_0                                                                          bad  ...                                    36.8075
    >>> valid_sequences_ratio
    {'F_clean_inversed_lowpassed_zscored_SCL_median': 0.0,
     'F_clean_inversed_lowpassed_zscored_SCL_std': 1.0,
     'F_clean_inversed_lowpassed_zscored_SCL_ptp': 1.0,
     'F_clean_inversed_lowpassed_zscored_SCL_linregress_slope': 1.0,
     'F_clean_inversed_lowpassed_zscored_SCL_linregress_rvalue': 1.0,
     'F_clean_inversed_lowpassed_zscored_SCL_auc': 1.0}
    """
    if not set(sequences).issubset(set(features.index)):
        logger.warning('Cannot find all pseudo-baseline sequences. Missing: %s',
                       list(set(sequences) - set(features.index)))

    columns = columns or features.columns
    if not set(columns).issubset(set(features.columns)):
        raise ValueError('Cannot find all columns in features. Missing: %s',
                         list(set(columns) - set(features.columns)))
    # Intersection between available sequences in the sequences report and the
    # pseudo-baseline sequences
    available_pseudo_baselines = list(set(sequences) & set(features.index))
    # Select the features amongst pseudo-baseline sequences and mask the values
    # that are not scalars (eg. 'bad' or else)
    features_baseline = features.loc[available_pseudo_baselines, :]
    features_baseline = features_baseline.where(
        features_baseline.applymap(lambda x: isinstance(x, (int, float, np.int64, np.float64))), other=np.NaN)
    # Compute the ratio of available samples per sequence in the pseudo-baseline
    # (0 if their were no good samples to estimate the average over the sequence, 1
    # if all samples could be considered.
    valid_sequences_ratio = (1 - features_baseline.isna().mean()).to_dict()
    valid_sequences_ratio = {column: valid_sequences_ratio[column] for column in columns}
    features_baseline_averaged = features_baseline.mean()

    def safe_substraction(original, value_to_substract):
        '''Substract a value to an original scalar
        If `original` is a scalar, then substract the `value_to_substract` ,
        else return `original`.

        Parameters
        ----------
        original: scalar from which the value should be substracted
        value_to_substract: value to substract

        '''
        if isinstance(original, (int, float, np.int64, np.float64)):
            return original - value_to_substract
        else:
            return original

    features_corrected = features.copy()
    for column in columns:
        correction = features_baseline_averaged[column]
        features_corrected[[column]] = features_corrected[[column]].applymap(lambda x: safe_substraction(x, correction))
    return features_corrected, valid_sequences_ratio