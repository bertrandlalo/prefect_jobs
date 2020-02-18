import logging
from typing import Tuple

import numpy as np
import pandas as pd
import scipy.signal
import scipy.stats

# from dsu.dsp.filters import filtfilt_signal
from dsu.dsp.resample import uniform_sampling
from dsu.epoch import sliding_window
from dsu.pandas_helpers import estimate_rate

# from iguazu.functions.common import verify_monotonic
# noinspection PyUnresolvedReferences
from iguazu.functions.hrv import hrv_features  # Alias to keep hrv in cardiac

logger = logging.getLogger(__name__)


# def ppg_clean(data, events, column, warmup_duration, filter_kwargs, sampling_rate):
#
#     verify_monotonic(events, 'events')
#     warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
#     begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
#     ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session
#
#     # truncate dataframe on session times
#     data = data[begins:ends]
#     data = data.loc[:, [column]]
#
#     # Estimate the sampling frequency: weird signals that have a heavy jitter
#     # will fail here early and raise a ValueError. See issue #44
#     fs = estimate_rate(data)
#
#     # resample uniformly the data
#     logger.debug('Uniform resampling from %.3f Hz to %d Hz', fs, sampling_rate)
#     data = uniform_sampling(data, sampling_rate)
#
#     # bandpass filter signal
#     # TODO: do we really want to be *that* flexible and accept any filtering
#     #       kwargs, or should we just force a band-pass at fixed frequencies
#     #       (a bit harsh maybe). Or maybe just receive two frequency values?
#     bp_bands = filter_kwargs.get('frequencies', [])
#     if len(bp_bands) != 2:
#         logger.warning('Expected two frequencies to do a bandpass filtering, '
#                        'but received %d', len(bp_bands))
#     logger.debug('Band-pass filtering to %s Hz', bp_bands)
#     data = filtfilt_signal(data, columns=[column],
#                            **filter_kwargs, suffix='_filtered')
#
#     # data = scale_signal(data, columns=[column + '_filtered'], suffix='_scaled',
#     #                     method='standard')
#
#     return data


def ssf(arr, win=64, fill_value=np.nan):
    """ Calculate the sum of slope function of a 1D array

    This function calculates the sum of slope function as defined by
    Jang et al. (2014).
    "A Real-Time Pulse Peak Detection Algorithm for the Photoplethysmogram."
    International Journal of Electronics and Electrical Engineering,
    https://doi.org/10.12720/ijeee.2.1.45-49

    Briefly, it calculates the first derivative of a signal and a windowed
    cumulative sum of the first derivative only when it is positive. This
    transformation enhances the first (systolic) peak of a PPG signal, enough
    to easily separate it from the second peak (after the diacrotic notch).

    Parameters
    ----------
    arr: np.ndarray
        A one-dimensional array representing the input signal.

    win: int
        The number of samples for the sliding window cumularive sum.

    fill_value: float
        Value to use when there is not enough data to calculate SSF, typically
        at the beginning of the signal until `win` samples have been read.

    Returns
    -------
    np.ndarray
        A one-dimensional numpy array with the same shape as `arr`.

    """
    x = np.asarray(arr)
    if x.ndim != 1:
        raise ValueError('ssf only supports 1D arrays')
    dx = np.diff(x, prepend=0)
    dx[dx <= 0] = 0
    dx_wins = sliding_window(dx, size=win, stepsize=1, copy=False)
    # shape of dx_wins is (n-win+1, win). The definition of ssf has the time
    # of each SSFi aligned to the leftmost sample. We need to add some NaNs (or
    # the fill value) to the right to fix the shape and the time
    ssf0 = dx_wins.sum(axis=1).astype(float)
    ssf1 = np.r_[np.repeat(fill_value, win - 1), ssf0]
    return ssf1


def detect_ssf_peaks(signal, *, fs=None, max_bpm=180, baseline_length=3, threshold_percentage=0.70, peak_memory_size=5):
    """ Detect peaks on a SSF signal

    This function performs the second part of the SSF-based PPG algorithm
    presented in
    Jang et al. (2014).
    "A Real-Time Pulse Peak Detection Algorithm for the Photoplethysmogram."
    International Journal of Electronics and Electrical Engineering,
    https://doi.org/10.12720/ijeee.2.1.45-49
    with some particularities that have been left out from this paper but are
    available on its previous iteration in
    Jang et al. (2014).
    "A robust method for pulse peak determination in a digital volume pulse waveform with a wandering baseline."
    IEEE Transactions on Biomedical Circuits and Systems,
    https://doi.org/10.1109/TBCAS.2013.2295102

    Briefly, it detects peaks on a SSF signal and then calculates and updates
    an adaptive threshold in order to keep only the most prominent peaks which
    correspond to PPG systolic peaks. The threshold is adaptative to account
    for a wandering baseline present on long PPG recordings. Initially, the
    threshold is set to a fraction of the max peaks on a baseline period. After
    this period, the threshold is updated every time a new peak is detected over
    the threshold.

    The timing of the SSF signal is important for this algorithm. For this
    reason, the input cannot be a numpy array; it must be a
    :py:class:`pandas.Series` whose index are timestamps.

    Parameters
    ----------
    signal: pd.Series
        Input SSF signal with timestamps as index
    fs: float, optional
        Sampling frequency. If not set, it will be deduced from the `signal` index.
    max_bpm: float
        Expected maximum number for beats per minute. This value is used to
        avoid peaks that are too close to each other.
    baseline_length: float
        Length of the baseline period to initialize the adaptive threshold.
    threshold_percentage: float
        Fraction of the maximum or median peak used to update the threshold.
    peak_memory_size: int
        Number of peaks to keep in memory to update the threshold.

    Returns
    -------
    peak_series: pd.Series
        A series with the PPG values where peaks were detected. The index of
        this series can be used to estimate beat-to-beat segments.
    threshold_series: pd.Series
        A series with the values of the dynamic threshold.

    """
    if fs is None:
        fs = estimate_rate(signal)
    if threshold_percentage < 0:
        raise ValueError('threshold_percentage must be positive')

    # Some synonyms for shorter code
    min_dist = int(max_bpm * 60 / fs)
    memsize = peak_memory_size
    memratio = threshold_percentage

    # Peak detection on complete signal, all at once
    i_peaks, props = scipy.signal.find_peaks(signal.values,
                                             distance=min_dist,
                                             prominence=1e-2,
                                             plateau_size=0)
    # Use the left edge of the peak since SSF often a plateau
    idx_peaks = signal.index[props['left_edges']]

    # Calculate initial threshold on a baseline.
    # On the original paper, this is done on the first 3 seconds of the SSF signal,
    # using 70% of the max peak on this baseline
    baseline_start = signal.index[0]
    baseline_end = signal.index[0] + np.timedelta64(baseline_length, 's')
    baseline = signal[baseline_start:baseline_end]
    threshold = np.nan_to_num(baseline[idx_peaks].max() * memratio, nan=0)

    # Keep a peak and threshold series
    peaks_series = baseline[baseline > threshold][idx_peaks].dropna().rename('peaks')
    threshold_series = pd.Series([threshold], index=[baseline_start], name='threshold')

    for index, value in signal.loc[baseline_end:][idx_peaks].items():
        if value > threshold:
            peaks_series.at[index] = value
            # Update the threshold to use the last N peaks. On the original paper
            # the details are lost but there is a reference that indicates that
            # it should be the 70% the median of the last 5 peaks
            threshold = np.nan_to_num(peaks_series.tail(n=memsize).median() * memratio, nan=0)
            threshold_series.at[index] = threshold

    return peaks_series, threshold_series


def extract_all_peaks(series: pd.Series, window_size: int = 512) -> Tuple[pd.DataFrame, pd.DataFrame]:
    n_samples = series.shape[0]
    # From https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
    # before using find_peaks, NaNs should either be removed or replaced.
    series = series.fillna(0)

    # Extract properties with a super-permissive find_peaks
    peaks, properties = scipy.signal.find_peaks(series,
                                                height=-np.Inf,
                                                threshold=-np.Inf,
                                                distance=1,
                                                prominence=0,
                                                width=0,
                                                plateau_size=0,
                                                )
    df_props = pd.DataFrame(properties)
    df_props.insert(0, 'index', series.index[peaks])
    df_props.insert(1, 'peak_sample', peaks)
    df_props.set_index('index', inplace=True)

    # Extract all peaks by creating a sliding window and then indexing with the
    # peaks obtained just before. Keep only the peaks that have a
    # complete window
    complete_peaks = peaks[(peaks - window_size // 2 >= 0) & (peaks + window_size // 2 < n_samples)]
    sample_number = np.arange(n_samples)
    idx_all_window_samples = sliding_window(sample_number, size=window_size, stepsize=1, copy=False)
    idx_peak_window_samples = idx_all_window_samples[complete_peaks - window_size // 2]

    sample_peaks = series.values[idx_peak_window_samples]
    peak_number = np.repeat(complete_peaks, window_size)
    relative_sample = np.tile(np.arange(window_size) - window_size // 2, sample_peaks.shape[0])

    df_extracts = pd.DataFrame({'relative_sample': relative_sample,
                                series.name: sample_peaks.ravel()},
                               index=peak_number).rename_axis(index='peak')
    return df_props, df_extracts


def ppg_peak_detection(ppg):
    # Original peak finding approach by AK
    from datascience_utils.filters import scale_signal as scale_signal_deprecated
    ppg_scaled = scale_signal_deprecated(ppg, method='minmax', win=8)
    peaks, _ = scipy.signal.find_peaks(ppg_scaled, prominence=0.4, width=10)

    return peaks


def peak_to_nn(peaks: pd.Series, diff_percentage: int = 25, interval_range=(0.6, 1.3)):
    """ Convert peaks to NN intervals

    This function converts input peaks into NN intervals and then applies two
    artifact detection strategies to avoid false positives. The first strategy
    is to remove intervals with non-physiological values. The second strategy
    is to remove intervals whose change with respect to the previous one is
    over a certain ratio.

    Parameters
    ----------
    peaks: pd.Series
        Input series, with the same shape and index as :py:ref:`detect_ssf_peaks`.
    diff_percentage: float
        Maximum percentage difference accepted between two consecutive beats.
    interval_range: tuple
        Mininum and maximum values for acceptable physiological NN values, in
        seconds.

    Returns
    -------
    pd.DataFrame
        A pandas dataframe with columns `interval`, `bad` and `details` that
        includes, respectively, all NN intervals in milliseconds, a boolean
        that marks an interval as acceptable or not, and details concerning
        the rejection of each interval, if applicable.

    """
    if not (0 < diff_percentage < 100):
        raise ValueError('diff_percentage must be in the (0, 100) range, non-inclusive')
    min_nn, max_nn = np.asarray(interval_range) * 1000

    # Convert peaks (units: sample number) to intervals (units: milliseconds)
    time_ms = (peaks.index - peaks.index[0]) / np.timedelta64(1, 'ms')
    intervals = np.diff(time_ms)

    # Prepare the dataframe where the intervals will be saved
    df_int = pd.DataFrame(
        data=dict(
            interval=intervals,
            bad=False,
            details='OK',
        ),
        # Note on the index: drop the first peak because it has no previous peak reference
        # index=signal.index[peaks[1:]],
        index=peaks.index[1:],
    )

    # First artifact detection + rejection strategy:
    # "Remove RR intervals that differ more than 25% from the previous one"
    #
    # In NeuroKit, this is done with a loop as (paraphrasing):
    # if RR[index] < RR[index-1] * 0.75 or RR[index] > RR[index-1] * 1.25:
    #     ... detect as artifact ...
    #
    # Here, I am doing it without loops by developing these equations and
    # assumming that RR is strictly positive (> 0):
    # divide by RR[index-1], then apply log to get:
    # log(RR[index]) - log(RR[index-1]) < log(3/4)  or ... > log(5/4)
    #
    # Note this procedure is repeated several times until nothing is removed or
    # a maximum number of repetitions is reached
    diff_ratio = diff_percentage / 100
    N_REPETITIONS = 1
    for i in range(N_REPETITIONS):
        good = df_int.loc[~df_int.bad]
        log_rel_diff = np.log(good['interval']).diff()
        bool_artifacts = (
            (log_rel_diff < np.log(1 - diff_ratio)) |
            (log_rel_diff > np.log(1 + diff_ratio))
        )
        if np.sum(bool_artifacts) == 0:
            logger.debug('After %d iterations, no more PP artifact rejection due '
                         'to relative difference', i+1)
            break
        idx_artifacts = good.loc[bool_artifacts].index
        df_int.loc[idx_artifacts, 'bad'] = True
        df_int.loc[idx_artifacts, 'details'] = f'Rejected: Delta interval > {diff_percentage}% (iteration {i+1})'

    # Second artifact + rejection detection:
    # "Physiological"
    # Remove PP peaks that are not "normal", according to a publication
    idx_not_physiological = df_int.loc[
        (~df_int.bad) &                # From the remaining good PPs...
        (df_int.interval < min_nn) &   # detect intervals that are too short
        (df_int.interval > max_nn)     # detect intervals that are too long
    ]
    df_int.loc[idx_not_physiological, 'bad'] = True
    df_int.loc[idx_not_physiological, 'details'] = f'Rejected: outside physiological range ({600} - {1300} ms)'

    # Show a summary on the logs
    summary = (
        df_int.groupby('details').size()
        .to_frame(name='number of intervals')
        .assign(percentage=lambda x: 100 * x / df_int.shape[0])
    )
    logger.info('NN artifact detection summary:\n%s', summary.to_string())

    return df_int


def nn_interpolation(dataframe, fs, column='RR'):
    """ Interpolate a NN series to a uniformly-sampled series

    This function takes the acceptable NN intervals and applies a pchip
    interpolation to obtain a uniformly-sampled signal

    Parameters
    ----------
    dataframe: pd.DataFrame
        Input dataframe with NN intervals. If this dataframe has a column named
        `bad`, it will remove any interval that evaluate ``True`` on said column.
        The idea is to use this function with the result of
        :py:ref:`peak_to_nn`.
    fs: float
        Target sampling rate for the output dataframe.
    column: str
        Column that contains the NN intervals.

    Returns
    -------
    pd.DataFrame
        Dataframe with the uniformly-sampled NN intervals.

    """
    # Remove bad RRs
    if 'bad' in dataframe.columns:
        logger.debug('Removing %d/%d bad intervals', dataframe.bad.sum(), dataframe.shape[0])
        dataframe = dataframe.loc[~dataframe.bad]
    else:
        logger.debug('No interval removed due to missing "bad" column')

    if dataframe.shape[0] < 2:
        logger.warning('Cannot interpolate intervals, did not receive enough clean intervals')
        return pd.DataFrame()

    dataframe = dataframe[[column]]

    # We want to interpolate with pchip, but we cannot send this directly to
    # uniform_sampling (at least not without some important recoding of
    # uniform_sampling). The soluation here is to use sample-and-hold
    # (zero order interpolation) to generate the time index, then clear the
    # interpolated values and then use pandas interpolate, which accepts pchip
    tmp = uniform_sampling(dataframe, fs, interpolation_kind='zero')
    tmp[~tmp.index.isin(dataframe.index)] = np.nan
    dataframe_interp = (
        tmp
        .interpolate(method='pchip')
        .rename(columns={column: f'{column}i'})
    )

    return dataframe_interp
