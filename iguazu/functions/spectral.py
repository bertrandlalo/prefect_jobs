import logging

import numpy as np
import pandas as pd
from dsu.pandas_helpers import estimate_rate
from scipy.signal.spectral import _spectral_helper


logger = logging.getLogger(__name__)


def bandpower(data, bands, epoch_size, epoch_overlap, log=False):

    fs = int(estimate_rate(data))
    logger.debug('Calculating spectra with fs=%dHz on data shaped as %s',
                 fs, data.shape)

    x = data.values.T
    nperseg = epoch_size * fs
    noverlap = epoch_overlap * fs
    freqs, t, pxx = _spectral_helper(x, x, fs=fs, window='hann',
                                     nperseg=nperseg, noverlap=noverlap,
                                     detrend='constant', return_onesided=True,
                                     scaling='spectrum', mode='psd')  # TODO: psd or stft ???
    index = data.index[0] + pd.to_timedelta(t, unit='s')
    n = index.shape[0]

    if log:
        pxx = np.log(pxx)

    powers = []
    for name, (f_start, f_stop) in bands.items():
        f_start = f_start or 0
        f_stop = f_stop or fs / 2
        idx = (freqs >= f_start) & (freqs < f_stop)
        if idx.sum() == 0:
            logger.warning('Band %s is empty for fs=%d and nperseg=%d',
                           name, fs, nperseg)
            result = pd.DataFrame(data=[[np.nan] * len(data.columns)] * n,
                                  columns=data.columns,
                                  index=index)
        else:
            logger.debug('Calculating band power for %s with %d bins',
                         name, idx.sum())
            # pxx axes: (column, freq, time)
            power_sum = pxx[:, idx, :].sum(axis=1)
            # power_sum axes: (column, time)
            result = pd.DataFrame(data=power_sum.T,  # (time, column)
                                  columns=data.columns,
                                  index=index)

        powers.append(result.add_suffix(f'_{name}'))

    return pd.concat(powers, axis='columns')
