import logging

import numpy as np
import pandas as pd
from datascience_utils.cvxEDA import apply_cvxEDA
from datascience_utils.filters import scipy_filter_signal, scipy_scale_signal
from datascience_utils.peaks import OfflinePeak
from datascience_utils.signal_quality import label_bad_from_amplitude
from sklearn.preprocessing import RobustScaler

from iguazu.helpers.decorators import processify


logger = logging.getLogger(__name__)



def galvanic_clean(data, events, column, warmup_duration, glitch_kwargs, interpolation_kwargs, filter_kwargs,
                   scaling_kwargs, corrupted_maxratio):
    """
     Preprocess the galvanic data and detect bad quality samples.
     It should be noted that some steps here are specific to the device we use, ie. Nexus from MindMedia.
     Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
     devices might have different behaviors.

    The pipeline will:

        - detect bad samples calling :py:func:dsu.quality.detect_bad_from_amplitude with `glitch_kwargs`
        - remove the bad samples and evaluate the corruption ratio. If too high, then raise an error.
        - interpolate the missing signal e calling :py:meth:pandas.Series.interpolat with `interpolation_kwargs`.
        - inverse the signal to access galvanic conductance (G=1/R)
        - lowpass the resulting signal using :py:func:dsu.filters.dsp.bandpass_signal with `filter_kwargs`
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
    glitch_kwargs:
        Kkeywords arguments to detect bad samples.
    interpolation_kwargs:
        Keywords arguments to interpolate the missing (bad) samples.
    filter_kwargs:
        Keywords arguments to lowpass the data.
    scaling_kwargs:
        Keywords arguments to scale the data.
    corrupted_maxratio: float
        Maximum acceptable ratio of corrupted (bad) samples.

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

    begins = events.index[0] - np.timedelta64(1,
                                              's') * warmup_duration  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + np.timedelta64(1,
                                             's') * warmup_duration  # end 30 seconds after the beginning of the session

    # troncate dataframe on session times
    data = data[begins:ends]
    data = data.loc[:, [column]]

    # add a column "bad" with rejection boolean on amplitude criteria
    label_bad_from_amplitude(data, column_name=column, output_column='bad', inplace=True,
                             **glitch_kwargs)
    # label 0.0 values as bad
    data.loc[data.loc[:, column] == 0.0, 'bad'] = True

    # make a copy of the signal with suffix "_clean", mask bad samples
    data_clean = data[[column]].copy().add_suffix('_clean')
    data_clean.mask(data.bad, inplace=True)

    # estimate the corrupted ratio
    # if too many samples were dropped, raise an error
    corrupted_ratio = data.bad.mean()
    if corrupted_ratio > corrupted_maxratio:
        raise Exception('AO saturation of {corrupted_ratio} exceeds {maxratio}.'.format(corrupted_ratio=corrupted_ratio,
                                                                                        maxratio=corrupted_maxratio))

    # interpolate the signal
    begins = data_clean.first_valid_index()
    ends = data_clean.last_valid_index()
    data_clean = data_clean[begins:ends]

    # take inverse to have the SKIN CONDUCTANCE G = 1/R = I/U
    data_clean_inversed = 1 / data_clean.copy().add_suffix('_inversed')

    data_clean_inversed.interpolate(**interpolation_kwargs, inplace=True)

    # lowpass filter signal
    scipy_filter_signal(data_clean_inversed, columns=[column + '_clean_inversed'], btype='lowpass',
                        **filter_kwargs, suffix='lowpassed', inplace=True)

    # scale signal on the all session
    scipy_scale_signal(data_clean_inversed, columns=[column + '_clean_inversed_lowpassed'], suffix='zscored',
                       inplace=True, **scaling_kwargs)

    # return preprocessed data
    data = pd.concat([data, data_clean, data_clean_inversed], axis=1)
    return data


@processify
def galvanic_cvx(data, column, warmup_duration, glitch_params, cvxeda_params=None):
    """ Separate phasic (SCR) and tonic (SCL) galvanic components using a convexe deconvolution.

    Parameters
    ----------
    data: pd.ataFrame
        Dataframe containing the preprocessed GSR in channel given by column_name.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    glitch_params:
        Keywords arguments to detect bad samples.
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

    data = data.iloc[::2]
    data = apply_cvxEDA(data[[column]].dropna(), column_name=column, kwargs=cvxeda_params)

    # add a column "bad" with rejection boolean on amplitude criteria
    label_bad_from_amplitude(data, column_name=column + '_SCR',
                             output_column='bad', inplace=True, **glitch_params)
    # set warmup period to "bad"
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    # TODO: this does not do what it's supposed to do; it should be a slice!
    data.loc[:data.index[0] + warm_up_timedelta, 'bad'] = True
    data.loc[data.index[-1] - warm_up_timedelta:, 'bad'] = True
    return data


def galvanic_scrpeaks(data, column, warmup_duration, peaks_kwargs, glitch_kwargs):
    """ Detect peaks of SCR component and estimate their characteristics.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the deconvoluted GSR in channel given by column_name.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    peaks_kwargs:
        Keywords arguments to detect peaks and define their characteristics.
    glitch_kwargs:
        Keywords arguments to detect false detected peaks.

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
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    data = data.loc[:, [column]]
    data = data[data.index[0] + warm_up_timedelta:data.index[-1] - warm_up_timedelta]
    data.columns = ["SCR"]  # rename the column for simplicity purpose
    scaler = RobustScaler(with_centering=True, quantile_range=(5, 95.0))
    peakdetector = OfflinePeak(data, column_name='SCR', scaler=scaler, **peaks_kwargs)
    peakdetector.simulation()

    data = peakdetector._data.loc[:,
           ['SCR', 'peaks', 'peaks_left_locals', 'peaks_left_prominences', 'peaks_width_heights']].loc[
           peakdetector.peaks[0], :]
    data.columns = ['SCR', 'SCR_peaks_detected', 'SCR_peaks_increase-duration',
                    'SCR_peaks_increase-amplitude',
                    'SCR_peaks_recovery-duration']

    label_bad_from_amplitude(data, column_name='SCR_peaks_increase-duration', output_column='bad',
                             inplace=True, **glitch_kwargs)
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

    available_pseudo_baselines = list(set(sequences) & set(features.index))
    features_baseline = features.loc[available_pseudo_baselines, :]
    features_baseline = features_baseline.where(
        features_baseline.applymap(lambda x: isinstance(x, (int, float, np.int64, np.float64))), other=np.NaN)
    valid_sequences_ratio = (1 - features_baseline.isna().mean()).to_dict()
    valid_sequences_ratio = {column: valid_sequences_ratio[column] for column in columns}
    features_baseline_averaged = features_baseline.mean()

    def safe_substraction(x, correction):
        if isinstance(x, (int, float, np.int64, np.float64)):
            return x - correction
        else:
            return x

    features_corrected = features.copy()
    for column in columns:
        correction = features_baseline_averaged[column]
        features_corrected[[column]] = features_corrected[[column]].applymap(lambda x: safe_substraction(x, correction))
    return features_corrected, valid_sequences_ratio
