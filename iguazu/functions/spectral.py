import logging

import numpy as np
import pandas as pd
from dsu.pandas_helpers import estimate_rate
from scipy.integrate import simps
from scipy.signal.spectral import _spectral_helper


logger = logging.getLogger(__name__)


def bandpower(data, bands, epoch_size, epoch_overlap, fs=None, scaling='density', relative=False):
    # Note: add to doc that epoch_size and epoch_overlap is in seconds
    # also,
    # TODO: add on documentation of estimate_rate that the output is in Hz

    if isinstance(data, (pd.DataFrame, pd.Series)) and isinstance(data.index, (pd.TimedeltaIndex, pd.DatetimeIndex)):
        datetime_index = True
        fs = fs or int(estimate_rate(data))
        if isinstance(data, pd.DataFrame):
            columns = data.columns
            x = np.asarray(data.values)
        else:
            columns = [data.name]
            x = np.asarray(data.values)[:, np.newaxis]
    else:
        datetime_index = False
        x = np.asarray(data)
        if x.ndim not in (1, 2):
            raise ValueError('bandpower only supports 1- or 2-dimensional data')
        elif x.ndim == 1:
            x = x[:, np.newaxis]
        columns = [f'x{i+1}' for i in range(x.shape[1])]
        fs = fs or 1

    logger.debug('Calculating %s spectra with fs=%dHz on data shaped as %s',
                 'relative' if relative else 'absolute', fs, data.shape)

    x = x.T
    nsamples = x.shape[1]
    nperseg = int(epoch_size * fs)
    noverlap = int(epoch_overlap * fs)
    if nperseg > nsamples:
        raise ValueError('Epoch size is larger than data')

    # To whom it may concern: according to the _spectral_helper code, the
    # difference between scaling='density' and 'spectrum' is just how the
    # window adjusts the final value. One uses the sum of squared values, the
    # other the square of the sum. The 'density' also divides by the fs (which
    # is why the units change to V^2 / Hz).
    # In my opinion, this is not very important as long as we are consistent
    freqs, t, psd = _spectral_helper(x, x, fs=fs, window='hann',
                                     nperseg=nperseg, noverlap=noverlap,
                                     detrend='constant', return_onesided=True,
                                     scaling=scaling, mode='psd')  # TODO: psd or stft ???

    # Manage index
    if datetime_index:
        index = data.index[0] + pd.to_timedelta(t, unit='s')
    else:
        #
        index = pd.Index((t * (nperseg - noverlap)).astype(int),
                         name='sample')
    n = index.shape[0]

    powers = []
    rel_suffix = '_rel' if relative else '_abs'
    for name, (f_start, f_stop) in bands.items():
        f_start = f_start or 0
        f_stop = f_stop or fs / 2
        idx = (freqs >= f_start) & (freqs < f_stop)
        if idx.sum() == 0:
            logger.warning('Band %s is empty for fs=%d and nperseg=%d',
                           name, fs, nperseg)
            result = pd.DataFrame(data=[[np.nan] * len(columns)] * n,
                                  columns=columns,
                                  index=index)
        else:
            logger.debug('Calculating band power for %s with %d bins',
                         name, idx.sum())
            if idx.sum() <= 1:
                logger.warning('Band power for %s will be zero because there '
                               'are not enough frequency points to calculate an '
                               'integral', name)
            # TODO: we should manage the 1-bin case, but how ?
            # pxx axes: (column, freq, time)
            # bp = psd[:, idx, :].sum(axis=1)
            bp = simps(psd[:, idx, :], freqs[idx], axis=1)

            if relative:
                bp /= simps(psd, freqs, axis=1)

            # power_sum axes: (column, time)
            result = pd.DataFrame(data=bp.T,  # (time, column)
                                  columns=columns,
                                  index=index)

        powers.append(result.add_suffix(f'_{name}{rel_suffix}'))

    return pd.concat(powers, axis='columns')
