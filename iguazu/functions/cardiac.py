import logging
from typing import Tuple

import numpy as np
import pandas as pd
import scipy.signal
import scipy.stats

from dsu.dsp.filters import filtfilt_signal, scale_signal
from dsu.dsp.resample import uniform_sampling
from dsu.epoch import sliding_window
from dsu.pandas_helpers import estimate_rate

from iguazu.functions.common import verify_monotonic
# noinspection PyUnresolvedReferences
from iguazu.functions.hrv import hrv_features  # Alias to keep hrv in cardiac

logger = logging.getLogger(__name__)


def ppg_clean(data, events, column, warmup_duration, filter_kwargs, sampling_rate):

    verify_monotonic(events, 'events')
    warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
    begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session

    # truncate dataframe on session times
    data = data[begins:ends]
    data = data.loc[:, [column]]

    # Estimate the sampling frequency: weird signals that have a heavy jitter
    # will fail here early and raise a ValueError. See issue #44
    fs = estimate_rate(data)

    # resample uniformly the data
    logger.debug('Uniform resampling from %.3f Hz to %d Hz', fs, sampling_rate)
    data = uniform_sampling(data, sampling_rate)

    # bandpass filter signal
    # TODO: do we really want to be *that* flexible and accept any filtering
    #       kwargs, or should we just force a band-pass at fixed frequencies
    #       (a bit harsh maybe). Or maybe just receive two frequency values?
    bp_bands = filter_kwargs.get('frequencies', [])
    if len(bp_bands) != 2:
        logger.warning('Expected two frequencies to do a bandpass filtering, '
                       'but received %d', len(bp_bands))
    logger.debug('Band-pass filtering to %s Hz', bp_bands)
    data = filtfilt_signal(data, columns=[column],
                           **filter_kwargs, suffix='_filtered')

    # data = scale_signal(data, columns=[column + '_filtered'], suffix='_scaled',
    #                     method='standard')

    return data


def ssf(arr, win=64, fill_value=np.nan):
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


# def ssf_dataframe(dataframe, column, win=64):
#     result = dataframe.copy()
#     new_col = f'{column}_ssf'
#     result[new_col] = 0
#     x_ssf = ssf(dataframe[column], win=win)
#     idx = result.index[win:]
#     result.loc[idx, new_col] = x_ssf
#     return result


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


def peak_to_rr(signal, peaks, fs: int, diff_percentage: int = 25):
    if not (0 < diff_percentage < 100):
        raise ValueError('diff_percentage must be in the (0, 100) range, non-inclusive')

    # Convert peaks (units: sample number) to intervals (units: milliseconds)
    pp = np.diff(peaks) * 1000 / fs

    # Prepare the dataframe where the RR will be saved
    df_rr = pd.DataFrame(
        data=dict(
            RR=pp,
            bad=False,
            details='OK',
        ),
        # Note on the index: drop the first peak because it has no previous peak reference
        index=signal.index[peaks[1:]],
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
    diff_ratio = diff_percentage / 100
    N_REPETITIONS = 1
    # TODO: this should be repeated several times until
    #       nothing is removed or a max number of repetitions
    for i in range(N_REPETITIONS):
        good = df_rr.loc[~df_rr.bad]
        log_rel_diff = np.log(good['RR']).diff()
        bool_artifacts = (
            (log_rel_diff < np.log(1 - diff_ratio)) |
            (log_rel_diff > np.log(1 + diff_ratio))
        )
        if np.sum(bool_artifacts) == 0:
            logger.debug('After %d iterations, no more RR artifact rejection due '
                         'to relative difference', i+1)
            break
        idx_artifacts = good.loc[bool_artifacts].index
        df_rr.loc[idx_artifacts, 'bad'] = True
        df_rr.loc[idx_artifacts, 'details'] = f'Rejected: Delta RR > {diff_percentage}% (iteration {i+1})'

    # Second artifact + rejection detection:
    # "Physiological"
    # Remove RR peaks that are not "normal", according to a publication
    idx_not_physiological = df_rr.loc[
        (~df_rr.bad) &        # From the remaining good RRs...
        (df_rr.RR < 600) &    # detect intervals that are too short
        (df_rr.RR > 1300)     # detect intervals that are too long
    ]
    df_rr.loc[idx_not_physiological, 'bad'] = True
    df_rr.loc[idx_not_physiological, 'details'] = f'Rejected: outside physiological range ({600} - {1300} ms)'

    # Show a summary on the logs
    summary = (
        df_rr.groupby('details').size()
        .to_frame(name='number of intervals')
        .assign(percentage=lambda x: 100 * x / df_rr.shape[0])
    )
    logger.info('RR artifact detection summary:\n%s', summary.to_string())

    return df_rr


def rr_interpolation(RR, fs):
    # Remove bad RRs
    logger.debug('Removing %d/%d bad RR intervals', RR.bad.sum(), RR.shape[0])
    RR = RR.loc[~RR.bad].drop(columns=['bad', 'details'])

    if RR.shape[0] < 2:
        logger.warning('Cannot interpolate RR, did not receive enough clean RR intervals')
        return pd.DataFrame()

    # We want to interpolate with pchip, but we cannot send this directly to
    # uniform_sampling (at least not without some important recoding of
    # uniform_sampling). So let's sample-and-hold, clear the interpolated
    # values and then use pandas interpolate
    tmp = uniform_sampling(RR, fs, interpolation_kind='zero')
    tmp[~tmp.index.isin(RR.index)] = np.nan
    RRi = (
        tmp
        .interpolate(method='pchip')
        .rename(columns={'RR': 'RRi'})
    )

    return RRi
