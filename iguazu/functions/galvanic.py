import logging

import numpy as np
import pandas as pd
from dsu.cvxEDA import apply_cvxEDA
from dsu.dsp.filters import filtfilt_signal, scale_signal, drop_rows
from dsu.dsp.peaks import detect_peaks
from dsu.epoch import sliding_window
from dsu.pandas_helpers import estimate_rate
from sklearn.preprocessing import RobustScaler

from iguazu.core.exceptions import IguazuError
from iguazu.functions.common import verify_monotonic

logger = logging.getLogger(__name__)


# TODO: delete this function that's no relevance now that we 'standardize' the signals/events before.
# def galvanic_prepare(data, events, input_column, output_column, session_labels, warmup_duration,
#                      sampling_rate, up, down, quality_kwargs, corrupted_maxratio=1, unit='ohm'):
#     """
#      Prepare the galvanic data to standardize data across devices.
#      This function renames the columns, truncate the data based on the first and last event timestamps
#      and detect bad quality samples.
#
#      It should be noted that the parameters chosen for this function are particularly
#      specific to the device we use, ie. Nexus from MindMedia.
#      Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
#      devices might have different behaviors. Same for the so-called 'glitches' those may appear only in some devices.
#
#     The pipeline will:
#         - resample signal at uniform rate (`sampling_rate`*`up`/`down`) using a polyphase filtering.
#         - detect bad samples calling :py:func:dsu.quality.detect_bad_from_amplitude with `glitch_kwargs`
#         - evaluate the corruption ratio. If too high, then raise an error.
#
#     Parameters
#     ----------
#     data: pd.DataFrame
#         Dataframe containing the raw GSR in channel given by `input_column`.
#     events: pd.DataFrame
#         Dataframe with 2 columns: [label, data], containing string labels and serialized meta giving the context of the labels.
#     session_labels: list|None
#        Labels of first and last events, to truncate the data. If None, the first and last timestamp of the events dataframe are considered.
#     input_column: str
#         Name of column where the data of interest are located.
#     output_column: str
#         Name of column to rename the data of interest.
#     warmup_duration: float
#         Duration (in s) to select before and after the vr session (to avoid side effects in the future
#     processing steps, ie. that we can then set to bad ).
#     sampling_rate: float
#         Sampling rate of the input signal, to resample it to (sampling_rate * up / down) using polyphase filtering.
#     up : int
#         The up-sampling factor.
#     down : int
#         The down-sampling factor.
#     quality_kwargs:
#         Keywords arguments to detect bad samples. This parameter depends on the device specifications.
#     corrupted_maxratio: float
#         Maximum acceptable ratio of corrupted (bad) samples.
#
#     Returns
#     -------
#     data: pd.DataFrame
#           Dataframe with columns 'gsr', 'gsr_clean', 'gsr_clean_inversed', 'gsr_clean_inversed_lowpassed',
#           'gsr_clean_inversed_lowpassed_zscored', 'bad'
#
#     """
#     # select and rename galvanic column
#     data = data.loc[:, [input_column]].rename(columns={input_column: output_column})
#
#     if not events.index.is_monotonic:
#         raise Exception('Events index should be monotonic. ')
#     warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
#     if session_labels is None:
#         begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
#         ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session
#     else:
#         if session_labels[0] not in events.label.values or session_labels[1] not in events.label.values:
#             raise IguazuError(f'Could not find labels {session_labels} in the events ')
#         begins = events[events.label == session_labels[0]].index[
#                      0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
#         ends = events[events.label == session_labels[1]].index[
#                    -1] + warmup_timedelta  # begin 30 seconds before the beginning of the session
#     # truncate dataframe on session times
#     data = data[begins:ends]
#
#     # resample uniformly the data using a polyphase filtering
#     logger.debug('Uniform resampling to %d Hz', sampling_rate)
#
#     data = poly_uniform_sampling(data, sampling_rate, up, down)
#     # add a column "bad" with rejection boolean on Amplifier and HF (glitches) criteria
#     logger.debug('Detecting amplifier saturation and glitches')
#     data = quality_gsr(data, column=output_column,
#                        **quality_kwargs)  # /!\ before, we had: column=column + '_filtered'  /!\
#     # estimate the corrupted ratio
#     # if too many samples were dropped, raise an error
#     corrupted_ratio = data.bad.mean()
#     if corrupted_ratio > corrupted_maxratio:
#         raise IguazuError(f'Artifact corruption of {corrupted_ratio * 100:.0f}% '
#                           f'exceeds {corrupted_maxratio * 100:.0f}%')
#     if unit == 'ohm':
#         # take inverse to have the SKIN CONDUCTANCE G = 1/R = I/U
#         logger.debug('Inverting signals')
#         data = inverse_signal(data, columns=['gsr'], suffix='')
#
#     return data
#

def galvanic_clean(data, events, annotations, column, warmup_duration, corrupted_maxratio,
                   interpolation_kwargs, filter_kwargs, scaling_kwargs):
    """
     Preprocess the galvanic data.
     It should be noted that some steps here are specific to the device we use, ie. Nexus from MindMedia.
     Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
     devices might have different behaviors.

    The pipeline will:

        - lowpass the resulting signal using :py:func:dsu.filters.dsp.bandpass_signal with `filter_kwargs`
        - remove the bad samples and interpolate the missing signal e calling :py:meth:pandas.Series.interpolat with `interpolation_kwargs`.
        - inverse the signal to access galvanic conductance (G=1/R)
        - scale the signal on the whole session using using :py:func:dsu.filters.dsp.scale_signal with `scaling_kwargs`

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the raw GSR samples (in channel given by column_name) and
        their rejection status (in column named 'bad' ) .
    column: str  #TODO: since it's now standardized, should we fix this to 'GSR'?
        Name of column where the data of interest are located.
    processing steps, ie. that we can then set to bad ).
    interpolation_kwargs:
        Keywords arguments to interpolate the missing (bad) samples.
    filter_kwargs:
        Keywords arguments to lowpass the data.
    scaling_kwargs:
        Keywords arguments to scale the data.

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns 'gsr', 'gsr_clean', 'gsr_clean_inversed', 'gsr_clean_inversed_lowpassed',
          'gsr_clean_inversed_lowpassed_zscored', 'bad'

    Examples
    --------

        .. image:: ../source/_static/examples/galvanic_functions/io_clean.png

    """

    verify_monotonic(events, 'events')
    warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
    begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session

    # truncate dataframe on session times
    data = data.loc[:, [column]]

    data.loc[:begins] = np.NaN
    data.loc[ends:] = np.NaN

    annotations.loc[:begins, [column]] = 'outside_session'
    annotations.loc[ends:, [column]] = 'outside_session'


    # estimate the corrupted ratio
    # if too many samples were dropped, raise an error
    # TODO/Question: do we keep raising an error when corrupted ratio is above a threshold?
    corrupted_ratio = (~annotations[annotations.GSR != 'outside_session'].replace('', np.NaN).isna()).mean()[0]
    if corrupted_ratio > corrupted_maxratio:
        raise IguazuError(f'Artifact corruption of {corrupted_ratio * 100:.0f}% '
                          f'exceeds {corrupted_maxratio * 100:.0f}%')

    # set as 'bad' samples that are more than 5  standard deviations from mean
    outliers = data[((data[column] - data[column].mean()) / data[column].std()).abs() > 5].dropna().index
    annotations.loc[outliers, column] = 'outliers'
    data.loc[outliers, column] = np.NaN

    # lowpass filter signal
    logger.debug('Filter with %s to %s Hz', filter_kwargs.get('filter_type', 'bandpass'),
                 filter_kwargs.get('frequencies', []))
    data = filtfilt_signal(data, columns=[column],
                           **filter_kwargs, suffix='_filtered')

    # bad sample interpolation
    logger.debug('Interpolating %d/%d bad samples', data[column].isna().sum(), data.shape[0])
    # make a copy of the signal with suffix "_clean", mask bad samples
    data_clean = data[[column + '_filtered']].copy().add_suffix('_clean')
    # Pandas does not like tz-aware timestamps when interpolating
    if data_clean.index.tzinfo is None:
        # old way: tz-naive
        data_clean.interpolate(**interpolation_kwargs, inplace=True)
    else:
        # new way: with timezone. Convert to tz-naive, interpolate, then back to tz-aware
        data_clean = (
            data_clean.set_index(data_clean.index.tz_convert(None))
                .interpolate(**interpolation_kwargs)
                .set_index(data_clean.index))

    # scale signal on the all session
    logger.debug('Rescaling signals')
    data_clean = scale_signal(data_clean, columns=[column + '_filtered_clean'], suffix='_zscored',
                              **scaling_kwargs)

    # return preprocessed data
    logger.debug('Concatenating clean and filtered signals')
    data = pd.concat([data, data_clean], axis=1)

    return data, annotations


def downsample(data, sampling_rate):
    # downsample by dropping rows
    # TODO consider if should we decimate? That is, lowpass filter first?
    logger.debug('Downsampling signal to %d Hz', sampling_rate)
    return drop_rows(data, sampling_rate)


def galvanic_cvx(data, annotations, column=None, warmup_duration=15, threshold_scr=4.0,
                 cvxeda_params=None, epoch_size=None, epoch_overlap=None):
    """ Separate galvanic components using a convex deconvolution.

    This function separates the phasic (SCR) and tonic (SCL) galvanic components
    using the cvxEDA algorithm.

    For large signals, the underlying library (cvx) is particularly heavy on
    memory usage. Also, since it uses C code, it holds and does not relase the
    Python global interpreter lock (GIL). This makes everything more difficult,
    in particular for Iguazu. In order to manage this, one can do the algorithm
    by epochs using both the `epoch_size` and `epoch_overlap` parameters.

    Parameters
    ----------
    data: pd.DataFrame
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
    epoch_size: float
        Size in seconds of the epoch size. When set to ``None``, cvxEDA will
        be applied only once on the whole signal.
    epoch_overlap: float
        Size in seconds of the epoch overlap. When set to ``None``, cvxEDA will
        be applied only once on the whole signal.

    Returns
    -------
    data: pd.DataFrame
        Dataframe with columns: `..._SCR`, `..._SCL` and `bad`.

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_deconvolution.png

    """
    cvxeda_params = cvxeda_params or {}

    # extract SCR and SCL component using deconvolution toolbox cvxEDA

    bad = ~annotations.replace('', np.NaN).isna()

    # if no column is specified, consider the first one
    column = column or data.columns[-1]

    n = data.shape[0]
    idx_epochs = np.arange(n)[np.newaxis, :]
    idx_warmup = slice(0, n)

    if epoch_size is not None and epoch_overlap is not None:
        fs = estimate_rate(data)
        n_warmup = int(warmup_duration * fs)
        n_epoch = int(epoch_size * fs) + n_warmup
        n_overlap = int(epoch_overlap * fs)
        logger.debug('Attempting to epoch signal of %d samples into epochs '
                     'of %d samples and %d overlap', n, n_epoch, n_overlap)

        if n < n_epoch + n_overlap:
            # Data is not big enough for window
            logger.debug('Cannot epoch into epochs of %d samples, signal is not '
                         'large enough. Falling back to complete implementation.',
                         n_epoch)
        else:
            idx_epochs = sliding_window(np.arange(n), size=n_epoch, stepsize=n_overlap)
            idx_warmup = slice(n_warmup, -n_warmup)
            logger.debug('cvxEDA epoched implementation with %d epochs', len(idx_epochs))

    else:
        logger.debug('cvxEDA complete implementation')

    epochs = []
    for i, idx in enumerate(idx_epochs):
        logger.debug('Epoch %d / %d', i+1, len(idx_epochs))
        input = data.iloc[idx][[column]].dropna()
        if not input.empty:
            chunk = (
                apply_cvxEDA(input, **cvxeda_params)
                    .iloc[idx_warmup]
                    .rename_axis(index='epoched_index')
                    .reset_index()
            )
            epochs.append(chunk)

    if not epochs:
        return pd.DataFrame(), pd.DataFrame()  # or None?

    data = (
        pd.concat(epochs, ignore_index=False)
        .groupby('epoched_index')
        .mean()
        .rename_axis(index=data.index.name)
    )

    # add an annotation rejection boolean on amplitude criteria
    # todo: helpers with inputs: data, annotations, and index or bool condition, that sets values in data to NaN and annotate in annotations
    annotations.loc[data[data[
                             column + '_SCR'] >= threshold_scr].index, 'GSR'] = 'CVX SCR outlier'  # Todo: question: should we add a new column?

    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    annotations.loc[:data.index[0] + warm_up_timedelta,
    'GSR'] = 'CVX wam up'  # Todo: question: should we add a new column?
    annotations.loc[data.index[-1] - warm_up_timedelta:,
    'GSR'] = 'CVX wam up'  # Todo: question: should we add a new column?
    # replace column string name by 'gsr' for lisibility purpose
    data.columns = data.columns.str.replace(column, 'gsr')

    return data, annotations


def galvanic_scrpeaks(data, annotations, column=None, warmup_duration=15, peaks_kwargs=None, max_increase_duration=7):
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

    # if 'bad' not in data:
    #     raise ValueError('Received data without a column named "bad"')
    #
    # bad = data.bad

    # if no column is specified, consider the first one
    column = column or data.columns[-2]

    # Select the data of interest
    data = data.loc[:, [column]]
    data = data[data.index[0] + warm_up_timedelta:data.index[-1] - warm_up_timedelta]

    # Define the scaler to apply before detecting peaks
    scaler = RobustScaler(with_centering=False, quantile_range=(5, 95.0))
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
    # data.loc[:, 'bad'] = bad
    # Update the bad column with this new find of artefact, being false peak detection
    # (when thee increase duration is greater than the prominence window,
    # it means no local minima has been found, hence the peak was not significant)
    data.loc[data[column + '_peaks_increase-duration'] >= max_increase_duration, 'bad'] = True
    # To ease the extraction of peak rate, let's add a column with boolean values
    # True if the peak is kept, False if not.
    data.loc[:, column + '_peaks_detected'] = ~data.bad

    return data, annotations


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
